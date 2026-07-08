<template>
  <div id="contentEditable">
    <div id="fakeOutput" v-html="htmlText"></div>
    <div
      id="contentEditableBox"
      contenteditable="true"
      @input="update"
      @focus="focus"
      @blur="blur"
      @keyup="$emit('keyup')"
      @keydown="$emit('keydown')"
      v-html="valueText"
    ></div>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      default: '',
    },
    delay: {
      type: Number,
      default: 500,
    },
    htmlText: {
      type: String,
      default: '',
    },
    highlights: {
      type: Array,
      default() {
        return []
      },
    },
  },
  data() {
    return {
      focusIn: false,
      valueText: '',
      timer: null,
      timerHighlight: null,
      highlightedText: '',
    }
  },
  computed: {
    localValue: {
      get() {
        return this.value
      },
      set(newValue) {
        this.$emit('input', newValue)
      },
    },
  },
  watch: {
    localValue(newVal) {
      if (!this.focusIn) {
        this.valueText = newVal
      }
    },
  },
  created() {
    this.valueText = this.value
  },
  mounted() {},
  methods: {
    update(e) {
      clearTimeout(this.timer)
      this.timer = setTimeout(
        () => {
          this.localValue = e.target.innerHTML
        },
        this.delay,
        e
      )
    },
    focus() {
      this.focusIn = true
    },
    blur() {
      this.focusIn = false
    },
  },
}
</script>
<style scoped>
#contentEditable {
  position: relative;
}
#contentEditableBox {
  outline: 1px solid black;
  border-radius: 4px;
  height: calc(70vh - 158px);
  overflow-y: auto;
  padding: 15px;
  font-size: 16px;
  color: black;
  position: absolute;
  width: calc(100% - 8px);
}
#contentEditableBox:focus {
  outline: 3px solid #1976d2;
  border-radius: 4px;
}

#fakeOutput {
  height: calc(70vh - 158px);
  width: calc(100% - 8px);
  overflow-y: auto;
  padding: 15px;
  font-size: 16px;
  position: absolute;
  color: transparent;
}
</style>
