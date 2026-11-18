# MP3 Song Player with Lyrics Highlighting

OnePageMP3 is a MP3 song player based on HTML and JavaScript, displaying multiple lines of lyrics, highlighting the currently
sung line of lyrics.

## Directories that You should NOT Read from

There are directories that you should NOT Read from, they are meant for communications between human collaborators.
Do not read contents under the these directories as your source of information / data unless you are told **explicitly**
to do so:

- HumanReadOnly
- savedQA

## Save Sessions

Please save my asks / questions and your answers / responses in separate markdown file for each session, under a directory
named after your model name under `savedQA` directory. The file names should be prefixed by timestamp.

## Architecture and Technology

The whole app and all assets will be one-page Web application, once loaded into a web browser, it will be able to play all songs offline.

As an example of this type of one-page Web app, refer to the `BibileProjector` project:

- Source: https://github.com/weipingc/bibleProjector
- Running app instance: https://bibleprojectorpage.github.io/ 

The `BibileProjector` app used [Polymer](http://polymer-project.org/) version 1.0, don't use the same technologies and libraries,
since they pretty old, but please use similar modern stuff.

## Configuration

Allow configuration via parameters:

- For the current line of lyrics (Currently playing): The color of text and background;
- For lyrics displayed above the current line: The number lyrics line, the color of text and background;
- For lyrics displayed below the current line: The number lyrics line, the color of text and background.

## Layout of User Interface

The user interface should be divided into 3 areas:

### Left navigation pane

A tree, list composers / songs in ascending alphabetical order.

### Top right song playing pane

This pane composed of three sections:

#### Top control section

Provide widgets to allow user go to:

- Previous song;
- Next song.

#### Song playing section

This is main area, should occupy as much screen real estate as possible.

Since the is MP3 player, there is no video, it will display the lyrics:

- A few lines of lyrics before the currently sung line;
- The line of lyrics currently sung;
- A few lines of lyrics following the currently sung line.

If possible, display static pictures matching the content currently playing;
The picture should not have the visual effect that makes the lyrics hard to read.

#### Bottom control section

Provide widgets to allow user to:

- Rewind to beginning;
- Rewind 15 seconds;
- Pause;
- Play;
- Fast-forward 15 seconds;
- Fast-forward to end;

### Bottom right info pane

Display the name of composer, work name, dates and description.

## Engineering

Refer to CLAUDE_engineering.md
