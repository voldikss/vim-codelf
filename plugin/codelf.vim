" ============================================================================
" FileName: codelf.vim
" Description:
" Author: voldikss <dyzplus@gmail.com>
" GitHub: https://github.com/voldikss
" ============================================================================


if exists('g:loaded_codelf')
  finish
endif
let g:loaded_codelf= 1
let g:codelf_status = ''

let g:codelf_enable_popup_menu = get(g:, 'codelf_enable_popup_menu', v:true)

command!  -nargs=? Codelf            call codelf#start(<f-args>)
command!  -nargs=? CodelfOpenBrowser call codelf#browser#open(<f-args>)
