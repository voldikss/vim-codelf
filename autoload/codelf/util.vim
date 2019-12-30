" ============================================================================
" FileName: util.vim
" Description:
" Author: voldikss <dyzplus@gmail.com>
" GitHub: https://github.com/voldikss
" ============================================================================

function! codelf#util#echo(group, msg) abort
  if a:msg == '' | return | endif
  execute 'echohl' a:group
  echo a:msg
  echon ' '
  echohl NONE
endfunction

function! codelf#util#echon(group, msg) abort
  if a:msg == '' | return | endif
  execute 'echohl' a:group
  echon a:msg
  echon ' '
  echohl NONE
endfunction

function! codelf#util#show_msg(message, ...) abort
  if a:0 == 0
    let msg_type = 'info'
  else
    let msg_type = a:1
  endif

  if type(a:message) != 1
    let message = string(a:message)
  else
    let message = a:message
  endif

  call codelf#util#echo('Constant', '[vim-codelf]')

  if msg_type == 'info'
    call codelf#util#echon('Normal', message)
  elseif msg_type == 'warning'
    call codelf#util#echon('WarningMsg', message)
  elseif msg_type == 'error'
    call codelf#util#echon('Error', message)
  endif
endfunction
