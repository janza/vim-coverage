"{{{ Init

let s:plugin = maktaba#plugin#Get('coverage')

"}}}

"{{{ coverage.py provider

let s:imported_python = 0

function! coverage#javascript#GetCloverProvider() abort
  let l:provider = {
      \ 'name': 'clover.xml'}

  function l:provider.IsAvailable(unused_filename) abort
    return 1
  endfunction

  function l:provider.GetCoverage(filename) abort
    if !s:imported_python
      try
        call maktaba#python#ImportModule(s:plugin, 'vim_coverage')
      catch /ERROR.*/
          throw maktaba#error#NotFound(
              \ "Couldn't import Python coverage module (%s). " .
              \ 'Install the coverage package and try again.', v:exception)
      endtry
      let s:imported_python = 1
    endif
    let l:coverage_data = maktaba#python#Eval(printf(
        \ 'vim_coverage.GetCoverage(".", %s)',
        \ string(a:filename)))
    let [l:covered_lines, l:uncovered_lines] = l:coverage_data
    return coverage#CreateReport(l:covered_lines, l:uncovered_lines, [])
  endfunction

  return l:provider
endfunction

