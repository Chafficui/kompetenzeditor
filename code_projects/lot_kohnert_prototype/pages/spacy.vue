<template>
  <v-container>
    <v-row>
      <v-col class="text-center">
        <v-btn class="ma-1" tile color="primary" @click="foobar0()"
          >get /ui</v-btn
        >
        <v-btn class="ma-1" tile color="primary" @click="foobar1()"
          >post and get /dep</v-btn
        >
        <v-btn class="ma-1" tile color="primary" @click="foobar3()"
          >post and get /ent</v-btn
        >
        <v-btn class="ma-1" tile color="primary" @click="foobar4()"
          >post and get /sents</v-btn
        >
        <v-btn class="ma-1" color="primary" tile @click="foobar2()"
          >post and get /sents_dep</v-btn
        >
        <v-btn class="ma-1" tile color="primary" @click="foobar5()"
          >get /models</v-btn
        >
        <v-btn class="ma-1" tile color="primary" @click="foobar7()"
          >get /version</v-btn
        >
      </v-col>
    </v-row>
    <v-row class="pa-3">
      <v-col v-if="bspText" class="ma-3 pa-3">
        basierend auf diesem Text: <br />
        Dies ist ein Test. Ich teste hiermit spaCy. Jemand schreibt einen Satz,
        der einen Nebensatz enhält. Die Lehrenden werden diese Anwendung bald
        nutzen können.
      </v-col>
      <v-col cols="12">
        <v-sheet
          color="grey lighten-1"
          class="pa-5"
          v-html="response"
        ></v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data: () => ({
    response: '',
    bspText: false,
    inputTxt:
      'Dies ist ein Test. Ich teste hiermit spaCy. Jemand schreibt einen Satz, der einen Nebensatz enhält. Die Lehrenden werden diese Anwendung bald nutzen können.',
  }),
  methods: {
    foobar0() {
      this.bspText = false
      this.response =
        "<a href='http://127.0.0.1:8080/ui/' target='_blank'>Die UI wird auf ''http://127.0.0.1:8080/ui/'' angezeigt.</a>"
    },
    foobar1() {
      const sendPostRequest = async () => {
        try {
          this.bspText = true
          const res = await this.$axios.post('/api/dep', {
            text: this.inputTxt,
            model: 'de_core_news_sm',
          })
          this.response = res.data
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
      }
      sendPostRequest()
    },
    foobar2() {
      const sendPostRequest = async () => {
        try {
          this.bspText = true
          const res = await this.$axios.post('/api/sents_dep', {
            text: this.inputTxt,
            model: 'de_core_news_sm',
          })
          this.response = res.data
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
      }
      sendPostRequest()
    },
    foobar3() {
      const sendPostRequest = async () => {
        try {
          this.bspText = true
          const res = await this.$axios.post('/api/ent', {
            text: this.inputTxt,
            model: 'de_core_news_sm',
          })
          this.response = res.data
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
      }
      sendPostRequest()
    },
    foobar4() {
      const sendPostRequest = async () => {
        try {
          this.bspText = true
          const res = await this.$axios.post('/api/sents', {
            text: this.inputTxt,
            model: 'de_core_news_sm',
          })
          this.response = res.data
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
      }
      sendPostRequest()
    },
    async foobar5() {
      this.bspText = false
      const res = await this.$axios.get('/api/models')
      this.response = res.data
      return res
    },
    async foobar7() {
      this.bspText = false
      const res = await this.$axios.get('/api/version')
      this.response = res.data
      return res
    },
  },
}
</script>
