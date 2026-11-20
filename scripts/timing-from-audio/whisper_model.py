"""Load an OpenAI Whisper model, on the Apple GPU (MPS) when available (see scripts/README.md).

openai-whisper does not run on MPS as is. load() applies these workarounds when the device is "mps":
- the sparse `alignment_heads` buffer cannot be moved to MPS: it is moved as a dense tensor, then the
  sparse CPU original is put back (word timestamps only read its indices);
- word timestamps run DTW in float64, which MPS lacks: the matrix is moved to the CPU first;
- PyTorch's scaled-dot-product attention on MPS can produce NaN logits: Whisper's own attention is used;
- sampling at temperature > 0 turns -inf logits into NaN on MPS: tokens are sampled on the CPU.
"""
import torch
import whisper
import whisper.decoding
import whisper.model
import whisper.timing


class _CpuCategorical:
    def __init__(self, logits):
        self.device = logits.device
        self.dist = torch.distributions.Categorical(logits=logits.cpu())

    def sample(self):
        return self.dist.sample().to(self.device)


def default_device():
    return "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")


def load(name="medium", device=None):
    device = device or default_device()
    model = whisper.load_model(name, device="cpu")
    if device != "mps":
        return model.to(device)
    whisper.decoding.Categorical = _CpuCategorical
    whisper.model.MultiHeadAttention.use_sdpa = False
    whisper.timing.dtw = lambda x: whisper.timing.dtw_cpu(x.cpu().double().numpy())
    heads = model.alignment_heads
    model.register_buffer("alignment_heads", heads.to_dense(), persistent=False)
    model = model.to("mps")
    model.register_buffer("alignment_heads", heads, persistent=False)
    return model


def transcribe(model, audio, prompt=None, beam=None):
    """Transcribe sung English with word timestamps.

    - The lyrics are the prompt, carried into every 30 s window, so Whisper expects the libretto's words.
    - Greedy decoding at temperature 0 (beam=None) is fast; beam search (e.g. beam=5) is several times
      slower and was not more useful.
    - sample_len caps each window at 72 tokens: in melismas Whisper tends to loop ("shall be exalted,
      shall be exalted, …") until the 224-token limit, which made decoding 10–30x slower.
    - no_speech_threshold=None: Whisper rates singing as "no speech" and would otherwise drop it.
    """
    return model.transcribe(
        audio, language="en", word_timestamps=True, fp16=False,
        condition_on_previous_text=False, initial_prompt=prompt or None, carry_initial_prompt=bool(prompt),
        beam_size=beam, best_of=None, temperature=0.0, sample_len=72, no_speech_threshold=None,
        verbose=None)
