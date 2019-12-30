" ============================================================================
" FileName: browser.vim
" Description:
" Author: voldikss <dyzplus@gmail.com>
" GitHub: https://github.com/voldikss
" ============================================================================

function! s:open_url(url) abort
  if has('win32') || has('win64') || has('win32unix')
    let cmd = 'rundll32 url.dll,FileProtocolHandler ' . shellescape(a:url)
  elseif has('mac') || has('macunix') || has('gui_macvim') || system('uname') =~? '^darwin'
    let cmd = 'open ' . shellescape(a:url)
  elseif executable('xdg-open')
    let cmd = 'xdg-open ' . shellescape(a:url)
  else
    call codelf#util#show_msg('Browser was not found', 'error')
    return
  endif

  if exists('*jobstart')
    call jobstart(cmd)
  elseif exists('*job_start')
    call job_start(cmd)
  else
    call system(cmd)
  endif
endfunction

function codelf#browser#open(...) abort
  let codelf_api = 'https://unbug.github.io/codelf/#'
  if a:0 == 0
    let word = expand('<cword>')
  else
    let word = a:1
  endif
  call s:open_url(codelf_api . word)
endfunction
