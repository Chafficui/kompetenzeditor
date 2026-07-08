export default (context, inject) => {
  const endofstring = (searchStr, findStr) => {
    return searchStr.lastIndexOf(findStr) > 0
      ? searchStr.lastIndexOf(findStr) + findStr.length
      : -1
  }
  inject('indexOfEnd', endofstring)
}
