/* Work data for OnePageMP3: loaded by app.js from its artist's workFiles list */
onePageMp3Work({
  id: "mozart-requiem",
  title: "Requiem",
  titleTranslation: "安魂曲",
  titleSort: "Requiem",
  language: "la",
  translationLanguage: "zh",
  year: 1791,
  opusNumber: "K. 626",
  premiered: "Vienna, 2 January 1793",
  premieredTranslation: "维也纳，1793年1月2日",
  thumbnail: "Mozart.jpg",  // shown when the work is selected, and for any movement without a picture of its own
  description: "Requiem Mass in D minor for soloists, chorus, orchestra and organ, on the Latin text of the Mass for the Dead. Left unfinished at Mozart's death on 5 December 1791 and completed by his pupil Franz Xaver Süssmayr.\nRecording: Edith Mathis, soprano; Julia Hamari, alto; Wiesław Ochman, tenor; Karl Ridderbusch, bass; Konzertvereinigung Wiener Staatsopernchor (chorus master Norbert Balatsch); Hans Haselböck, organ; Wiener Philharmoniker; Karl Böhm, conductor. Deutsche Grammophon 2530 143 (1 LP), 1971.\nSource: Internet Archive, https://archive.org/details/lp_requiem_volfgang-amadeus-mozart-karl-bhm-viener-ph",
  descriptionTranslation: "D小调安魂弥撒，为独唱、合唱、管弦乐队与管风琴而作，歌词为拉丁文追思弥撒经文。1791年12月5日莫扎特去世时尚未完成，由其学生弗朗茨·克萨韦尔·苏斯迈尔续完。\n录音：女高音伊迪丝·马蒂斯、女低音尤利娅·哈马里、男高音维斯瓦夫·奥赫曼、男低音卡尔·里德布施；维也纳国家歌剧院合唱团音乐会协会（合唱指导诺贝特·巴拉奇）；管风琴汉斯·哈泽尔伯克；维也纳爱乐乐团；指挥卡尔·伯姆。Deutsche Grammophon 2530 143（1张唱片），1971年。\n来源：Internet Archive, https://archive.org/details/lp_requiem_volfgang-amadeus-mozart-karl-bhm-viener-ph",
  // One movement per band of the LP; the numbers (1–12) are the ones printed on its sleeve.
  // Side 1 is a single band holding Nos. 1–7; side 2 has one band per number.
  movements: [
    {
      id: "ch1",
      number: "I",
      title: "Introitus, Kyrie, Sequentia",
      titleTranslation: "进台经、垂怜经、继抒咏",
      subtitle: "Nos. 1–7",
      subtitleTranslation: "第1–7首",
      voicing: "Chorus; soprano, alto, tenor, bass",
      voicingTranslation: "合唱；女高音、女低音、男高音、男低音",
      description: "1 Requiem aeternam – Kyrie (chorus, soprano); 2 Dies irae (chorus); 3 Tuba mirum (soloists); 4 Rex tremendae (chorus); 5 Recordare (soloists); 6 Confutatis (chorus); 7 Lacrimosa (chorus).",
      audio: "Chapter1.mp3",
      background: "Chapter1-bg.jpg"
    },
    {
      id: "ch2",
      number: "II",
      title: "Domine Jesu",
      titleTranslation: "主耶稣",
      subtitle: "No. 8 · Offertorium",
      subtitleTranslation: "第8首 · 奉献经",
      voicing: "Chorus; soprano, alto, tenor, bass",
      voicingTranslation: "合唱；女高音、女低音、男高音、男低音",
      description: "8 Domine Jesu (chorus, soloists), ending with the fugue Quam olim Abrahae.",
      audio: "Chapter2.mp3",
      background: "Chapter2-bg.jpg"
    },
    {
      id: "ch3",
      number: "III",
      title: "Hostias",
      titleTranslation: "祭献",
      subtitle: "No. 9 · Offertorium",
      subtitleTranslation: "第9首 · 奉献经",
      voicing: "Chorus",
      voicingTranslation: "合唱",
      description: "9 Hostias (chorus), ending with the fugue Quam olim Abrahae repeated from No. 8.",
      audio: "Chapter3.mp3",
      background: "Chapter3-bg.jpg"
    },
    {
      id: "ch4",
      number: "IV",
      title: "Sanctus",
      titleTranslation: "圣哉经",
      subtitle: "No. 10",
      subtitleTranslation: "第10首",
      voicing: "Chorus",
      voicingTranslation: "合唱",
      description: "10 Sanctus (chorus), ending with the fugue Hosanna in excelsis.",
      audio: "Chapter4.mp3",
      background: "Chapter4-bg.jpg"
    },
    {
      id: "ch5",
      number: "V",
      title: "Benedictus",
      titleTranslation: "降福经",
      subtitle: "No. 11",
      subtitleTranslation: "第11首",
      voicing: "Soprano, alto, tenor, bass; chorus",
      voicingTranslation: "女高音、女低音、男高音、男低音；合唱",
      description: "11 Benedictus (soloists), ending with the Hosanna fugue (chorus).",
      audio: "Chapter5.mp3",
      background: "Chapter5-bg.jpg"
    },
    {
      id: "ch6",
      number: "VI",
      title: "Agnus Dei, Lux aeterna",
      titleTranslation: "羔羊经、永恒之光",
      subtitle: "No. 12 · Agnus Dei, Communio",
      subtitleTranslation: "第12首 · 羔羊经、领主咏",
      voicing: "Chorus; soprano",
      voicingTranslation: "合唱；女高音",
      description: "12 Agnus Dei (chorus), followed by the Communio Lux aeterna (soprano, chorus), which returns to the music of the Introitus and the Kyrie fugue.",
      audio: "Chapter6.mp3",
      background: "Chapter6-bg.jpg"
    }
  ]
});
