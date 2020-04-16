" ========================================================================
" FileName: codelf.vim
" Description:
" Author: voldikss
" GitHub: https://github.com/voldikss
" ========================================================================

let s:py_file = expand('<sfile>:p:h') . '/../script/codelf.py'

if !exists('s:python_executable')
  if executable('python3')
    let s:python_executable = 'python3'
  elseif executable('python')
    let s:python_executable = 'python'
  elseif exists('g:python3_host_prog')
    let s:python_executable = g:python3_host_prog
  else
    call codelf#util#show_msg('Python is required but not found', 'error')
    finish
  endif
endif

if has('nvim')
  function! s:on_stdout_nvim(jobid, data, event) abort
    call s:callback(a:data)
  endfunction

  function! s:on_exit_nvim(jobid, code, event) abort
  endfunction
else
  function! s:on_stdout_vim(event, ch, msg) abort
    call s:callback(a:msg)
  endfunction

  function! s:on_exit_vim(ch, code) abort
  endfunction
endif

function! s:callback(data) abort
  let g:codelf_status = ''
  if type(a:data) == 3
    let message = join(a:data, ' ')
  else
    let message = a:data
  endif

  try
    let candidates = eval(message)
    if message ==# '' || type(candidates) != 3
      call codelf#util#show_msg('No queries', 'info')
      return
    endif
  catch /.*/
    return
  endtry

  call s:display(candidates)
endfunction

""
" Display the candidates in popup menu or inputlist
function! s:display(candidates) abort
  " If user moved the cursor, codelf displaying will be cancelled
  if exists('s:cursor_pos') && getpos('.') != s:cursor_pos
    call codelf#util#show_msg('Codelf cancelled since the cursor was moved', 'warning')
    return
  endif
  unlet s:cursor_pos

  if g:codelf_enable_popup_menu == v:true && mode() ==# 'i'
    let pos = col('.')
    normal! diw
    call complete(pos, a:candidates)
  else
    let candidates = ['Choose from:']
    for i in range(min([len(a:candidates), &lines-5]))
      call add(candidates, i . '. ' . a:candidates[i])
    endfor
    let selection = str2nr(inputlist(candidates))
    let reg_tmp = @a
    let @a = a:candidates[selection]
    normal! viw"ap
    let @a = reg_tmp
  endif
endfunction

function! s:job_start(cmd) abort
  if has('nvim')
    let callback = {
      \ 'on_stdout': function('s:on_stdout_nvim'),
      \ 'on_stderr': function('s:on_stdout_nvim'),
      \ 'on_exit': function('s:on_exit_nvim')
      \ }
    call jobstart(a:cmd, callback)
  else
    let callback = {
      \ 'out_cb': function('s:on_stdout_vim', ['stdout']),
      \ 'err_cb': function('s:on_stdout_vim', ['stderr']),
      \ 'exit_cb': function('s:on_exit_vim'),
      \ 'out_io': 'pipe',
      \ 'err_io': 'pipe',
      \ 'in_io': 'null',
      \ 'out_mode': 'nl',
      \ 'err_mode': 'nl',
      \ 'timeout': '2000'
      \ }
    call job_start(a:cmd, callback)
  endif
endfunction

function! codelf#start(...) abort
  let g:codelf_status = 'requesting codelf'
  let s:cursor_pos = getpos('.')
  if a:0 == 0
    let word = expand('<cword>')
  else
    let word = a:1
  endif
  let cmd = 'python3 ' . s:py_file . ' ' . word
  if g:codelf_enable_popup_menu == v:true
    startinsert
  endif
  call s:job_start(cmd)
  return ''
endfunction
