import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

const highlightPluginKey = new PluginKey('verbHighlight')

export const VerbHighlight = Extension.create({
  name: 'verbHighlight',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: highlightPluginKey,
        state: {
          init() {
            return DecorationSet.empty
          },
          apply(tr, oldState) {
            const meta = tr.getMeta(highlightPluginKey)
            if (meta) {
              const decorations = meta.highlights.map((h) => {
                const attrs = { class: h.class }
                if (h.title) attrs['data-tooltip'] = h.title
                return Decoration.inline(h.from, h.to, attrs)
              })
              return DecorationSet.create(tr.doc, decorations)
            }
            if (tr.docChanged) {
              return oldState.map(tr.mapping, tr.doc)
            }
            return oldState
          },
        },
        props: {
          decorations(state) {
            return this.getState(state)
          },
        },
      }),
    ]
  },
})

export function setVerbHighlights(editor, highlights) {
  if (!editor) return
  const tr = editor.state.tr
  tr.setMeta(highlightPluginKey, { highlights })
  editor.view.dispatch(tr)
}
