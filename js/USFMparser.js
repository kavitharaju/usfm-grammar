const match = require('./grammarOperations.js').match
const relaxParse = require('./grammarOperations-relaxed.js').relaxParse
const convert = require('./convert.js')

var warnings = []

function normalize (str) {
  let newStr = ''
  const multiLinePattern = new RegExp('[\\n\\r][\\n\\r]+', 'g')
  const multiSpacePattern = new RegExp('  +', 'g')
  const trailingSpacePattern = new RegExp(' +[\n\r]', 'g')
  const bookCodePattern = new RegExp('\\id ([a-z][a-z][a-z])[ \\n\\r]', 'g')
  if (multiLinePattern.exec(str)) {
    warnings.push('Empty lines present. ')
  }
  if (multiSpacePattern.exec(str)) {
    warnings.push('Multiple spaces present. ')
  }
  if (trailingSpacePattern.exec(str)) {
    warnings.push('Trailing spaces present at line end. ')
  }
  newStr = str.replace(trailingSpacePattern, '\n')
  newStr = newStr.replace(multiLinePattern, '\n')
  newStr = newStr.replace(multiSpacePattern, ' ')
  let match = bookCodePattern.exec(newStr)
  if (match) {
    let bookCode = match[1]
    newStr = newStr.replace(bookCode, bookCode.toUpperCase())
    warnings.push('Book code is in lowercase. ')
  }
  return newStr
}

exports.SCRIPTURE = 'clean'
exports.toCSV = 'csv'
exports.toTSV = 'tsv'

exports.parseUSFM = function (str, resultType = 'all', mode="normal") {
  if (mode == "normal") {
      warnings = []
      let inStr = normalize(str)
      let matchObj = match(inStr)

      if (!matchObj.hasOwnProperty('ERROR')) {
        let jsonOutput = matchObj['parseStructure']
        if (matchObj.warnings) {
          warnings = warnings.concat(matchObj['warnings'])
          // console.log(warnings)
        }
        if (resultType === 'clean') {
          let newJsonOutput = { 'book': jsonOutput['metadata']['id']['book'], 'chapters': [] }
          let chapter = {}
          for (let i = 0; i < jsonOutput['chapters'].length; i++) {
            chapter = jsonOutput['chapters'][i]
            let nextChapter = { 'chapterTitle': chapter['header']['title'], 'verses': [] }
            let verse = {}
            for (let j = 0; j < chapter['verses'].length; j++) {
              verse = chapter['verses'][j]
              let nextVerse = { 'verseNumber': verse['number'], verseText: verse['text'] }
              nextChapter['verses'].push(nextVerse)
            }
            newJsonOutput['chapters'].push(nextChapter)
          }
          jsonOutput = newJsonOutput
        }
        else if (resultType === 'csv'){
          var csvOutput = convert.getCSV(jsonOutput)
          return csvOutput
        }
        else if (resultType === 'tsv'){
          var tsvOutput = convert.getTSV(jsonOutput)
          return tsvOutput
        }
        if (warnings !== '') {
          jsonOutput['messages'] = { 'warnings': warnings }
        }
        return jsonOutput
      } else {
        return matchObj
      }
  }
  else if(mode == "relaxed"){
      console.log("coming into relaxed parsing")
      let parseObj = relaxParse(str)
      return parseObj
    }
}

exports.validate = function (str) {
  let inStr = normalize(str)
  // Matching the input with grammar and obtaining the JSON output string
  let matchObj = match(inStr)
  if (matchObj.hasOwnProperty('ERROR')) {
    return false
  } else {
    return true
  }
}
