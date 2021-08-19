// add specialized words to the lexion

loadFr();
dmf = require("../data/lexicon-dmf.json")
updateLexicon(dmf)
console.log("dmf loaded:%d entries",Object.keys(dmf).length)
// addToLexicon({"prévision":{"N":{"g":"f","tab":["n17"]}}})
// addToLexicon({"environnement":{ N: { g: 'm', tab: [ 'n3' ] } }})
// addToLexicon({"aujourd'hui":{ Adv: { tab: [ 'av' ] } }})
// addToLexicon({"prévu":{ A: { tab: [ 'n28' ] }, N: { g: 'm', tab: [ 'n3' ] } }})
// addToLexicon({"émettre":{"V":{"aux":["av"],"tab":"v89"}}})

loadEn();
addToLexicon({"gust":{"N":{"tab":["n5"]},"V":{"tab":"v1"}}})
