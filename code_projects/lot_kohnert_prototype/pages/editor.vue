<template>
  <v-row justify="center" align="center" no-gutters>
    <v-col cols="12" sm="8">
      <v-sheet outlined color="black" style="margin-top: -2px">
        <v-card class="pa-0" tile flat height="calc(70vh - 102px)">
          <v-toolbar flat dense tile>
            <v-text-field
              id="compTitle"
              v-model="compName"
              placeholder="Name ggfs. Modul"
              solo
              flat
              hide-details
              color="white"
              style="font-size: 1.6em; border-radius: 0px; width: 38vw"
            ></v-text-field>

            <v-spacer></v-spacer>
            <v-btn
              outlined
              color="primary"
              class="mr-1"
              @click="dialogAction = true"
            >
              <v-icon>mdi-content-save</v-icon>
              speichern
            </v-btn>

            <v-btn
              depressed
              color="primary"
              @click="
                dialogInfo = true
                textareaInfo = true
              "
            >
              <v-icon>mdi-information-outline</v-icon>
            </v-btn>
          </v-toolbar>
          <v-card-text class="pa-1" height="calc(70vh - 184px)">
            <Editable
              id="textBox"
              v-model="text"
              :delay="typingDelay"
              :htmlText="highlightedText"
              :highlights="highlight"
              @input="processHighlighted"
            />
          </v-card-text>
        </v-card>
      </v-sheet>
      <v-col cols="12" sm="12" class="pa-0">
        <v-sheet outlined color="black">
          <v-card outlined tile height="30vh">
            <v-toolbar flat dense tile>
              <v-toolbar-title>Bewertung</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn
                depressed
                color="primary"
                @click="
                  dialogInfo = true
                  scoreInfo = true
                "
              >
                <v-icon>mdi-information-outline</v-icon>
              </v-btn>
            </v-toolbar>
            <v-card-text style="overflow-y: auto; min-height: 230px">
              <v-row>
                <v-col cols="4" class="d-flex justify-center">
                  <v-progress-circular
                    :rotate="270"
                    :size="200"
                    :width="25"
                    :value="score"
                    color="blue-grey"
                  >
                    {{ score }} %
                  </v-progress-circular>
                </v-col>
                <v-col cols="8">
                  <v-list>
                    <v-divider></v-divider>
                    <v-list-item>
                      <v-list-item-content>
                        <v-chip
                          color="blue-grey lighten-4"
                          style="max-width: max-content"
                        >
                          Sätze insgesamt
                          <v-avatar right class="blue-grey lighten-3">
                            {{ nlpSentences.length }}
                          </v-avatar>
                        </v-chip>
                      </v-list-item-content>
                      <v-list-item-action class="my-0">
                        <v-menu
                          :close-on-content-click="false"
                          :nudge-width="100"
                          offset-x
                        >
                          <template v-slot:activator="{ on, attrs }">
                            <v-btn icon v-bind="attrs" v-on="on">
                              <v-icon color="grey lighten-1"
                                >mdi-information</v-icon
                              >
                            </v-btn>
                          </template>
                          <v-card width="350">
                            <v-card-text>
                              <p>
                                Der gesamte Text enthält
                                {{ nlpSentences.length }} Sätze.
                              </p>
                              <p>
                                Auf Basis der Gesamtanzahl wird die Wertung
                                errechnet. Jeder Satz kann eine positive oder
                                negative Bewertung bekommen und diese wird auf
                                den gesamt Wert (links zu finden) angerechnet.
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-menu>
                      </v-list-item-action>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item>
                      <v-list-item-content>
                        <v-chip
                          color="blue-grey lighten-4"
                          style="max-width: max-content"
                        >
                          entbehrliche Sätze
                          <v-avatar right style="background-color: yellow">
                            {{ noVerbsSents.length }}
                          </v-avatar>
                        </v-chip>
                      </v-list-item-content>
                      <v-list-item-action class="my-0">
                        <v-menu
                          :close-on-content-click="false"
                          :nudge-width="100"
                          offset-x
                        >
                          <template v-slot:activator="{ on, attrs }">
                            <v-btn icon v-bind="attrs" v-on="on">
                              <v-icon color="grey lighten-1"
                                >mdi-information</v-icon
                              >
                            </v-btn>
                          </template>
                          <v-card width="350">
                            <v-card-text>
                              <p>
                                Es wurden {{ noVerbsSents.length }} entbehrliche
                                Sätze erkannt.
                              </p>
                              <p>
                                Das wirkt sich negativ auf die Bewertung aus und
                                veringert diese um
                                <v-chip pill>{{ noVerbsSentsScore }}%</v-chip>
                              </p>
                              <p>
                                Ein entbehrlicher Satz, ist ein Satz, der weder
                                ein empfohlenes noch ein nicht empfohlenes Verb
                                enthält.
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-menu>
                      </v-list-item-action>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item>
                      <v-list-item-content>
                        <v-chip
                          color="blue-grey lighten-4"
                          style="max-width: max-content"
                        >
                          empfohlene Verben
                          <v-avatar right style="background-color: lightgreen">
                            {{ goodVerbsCount }}
                          </v-avatar>
                        </v-chip>
                      </v-list-item-content>
                      <v-list-item-action class="my-0">
                        <v-menu
                          :close-on-content-click="false"
                          :nudge-width="100"
                          offset-x
                        >
                          <template v-slot:activator="{ on, attrs }">
                            <v-btn icon v-bind="attrs" v-on="on">
                              <v-icon color="grey lighten-1"
                                >mdi-information</v-icon
                              >
                            </v-btn>
                          </template>
                          <v-card width="350">
                            <v-card-text>
                              <p>
                                Es wurden {{ goodVerbsCount }} empfohlene Verben
                                erkannt:
                              </p>
                              <p>
                                <v-simple-table
                                  fixed-header
                                  height="175px"
                                  dense
                                >
                                  <template v-slot:default>
                                    <tbody>
                                      <tr
                                        v-for="(
                                          item, index
                                        ) in allTextGoodVerbs"
                                        :key="index"
                                      >
                                        <td>{{ item }}</td>
                                      </tr>
                                    </tbody>
                                  </template>
                                </v-simple-table>
                              </p>
                              <p>
                                Ein Satz wird als positiv bewertet sobald dieser
                                ein empfohlenes Verb enthält. Nicht empfohlene
                                Verben überschreiben die positive Bewertung und
                                der Satz wird negativ bewertet.
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-menu>
                      </v-list-item-action>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item>
                      <v-list-item-content>
                        <v-chip
                          color="blue-grey lighten-4"
                          style="max-width: max-content"
                        >
                          nicht empfholene Verben
                          <v-avatar right style="background-color: lightcoral">
                            {{ badVerbsCount }}
                          </v-avatar>
                        </v-chip>
                      </v-list-item-content>
                      <v-list-item-action class="my-0">
                        <v-menu
                          :close-on-content-click="false"
                          :nudge-width="100"
                          offset-x
                        >
                          <template v-slot:activator="{ on, attrs }">
                            <v-btn icon v-bind="attrs" v-on="on">
                              <v-icon color="grey lighten-1"
                                >mdi-information</v-icon
                              >
                            </v-btn>
                          </template>
                          <v-card width="350">
                            <v-card-text>
                              <p>
                                Es wurden {{ badVerbsCount }} nicht empfohlene
                                Verben erkannt.
                              </p>
                              <p>
                                Das wirkt sich negativ auf die Bewertung aus und
                                veringert diese um
                                <v-chip pill>{{ badSentsScore }}%</v-chip>
                              </p>
                              <p>
                                Ein Satz wird als negativ bewertet dobald dieser
                                ein nicht empfohlenes Verb enthält. Ein
                                empfohlenes Verb in dem Satz hebt die negative
                                Wertung des Satzes nicht wieder auf.
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-menu>
                      </v-list-item-action>
                    </v-list-item>
                    <v-divider></v-divider>
                  </v-list>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-sheet>
      </v-col>
    </v-col>
    <v-col cols="12" sm="4">
      <v-sheet outlined color="black">
        <v-card
          outlined
          tile
          height="calc(100vh - 100px)"
          style="margin-top: -2px"
        >
          <v-toolbar flat dense tile>
            <v-toolbar-title>Vorschläge</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
              depressed
              color="primary"
              @click="
                dialogInfo = true
                suggentionsInfo = true
              "
            >
              <v-icon>mdi-information-outline</v-icon>
            </v-btn>
          </v-toolbar>
          <v-card-text style="overflow-y: overlay; height: calc(100vh - 162px)">
            <v-expansion-panels
              v-if="badVerbRule"
              v-model="suggPanels"
              focusable
              accordion
              multiple
              class="mb-5"
            >
              <v-expansion-panel
                v-for="(item, i) in allTextBadVerbs"
                :key="i"
                elevation="20"
              >
                <v-expansion-panel-header>
                  <v-row>
                    <v-col cols="12">
                      <v-chip
                        label
                        width="100%"
                        style="background-color: lightcoral"
                        >{{ item }}
                      </v-chip>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-card flat>
                    <v-card-text class="px-2">
                      <ul>
                        <li>
                          Vermeiden Sie verben wie "<b>{{ item }}</b
                          >".
                        </li>
                        <li>
                          Es ist nicht garantiert, dass die Studierenden nach
                          Teilnahme am Modul Sachverhalte direkt
                          <b>{{ item }}</b
                          >.
                        </li>
                        <li>
                          Das Verb <b>{{ item }}</b> ist nur schwer messbar.
                        </li>
                        <li>Nutzen Sie Verben, die gut messbar sind.</li>
                      </ul>
                      <div class="ma-4">
                        Hier finden Sie eine Auswahl an Verben, welche sich
                        besser eignen:
                      </div>
                      <v-expansion-panels>
                        <v-expansion-panel id="suggVerbsTable">
                          <v-expansion-panel-header color="blue-grey lighten-5"
                            >empfohlene Verben</v-expansion-panel-header
                          >
                          <v-expansion-panel-content style="padding: 0px">
                            <v-simple-table fixed-header height="350px" dense>
                              <template v-slot:default>
                                <thead>
                                  <tr>
                                    <th class="text-left">Taxonomiestufe</th>
                                    <th class="text-left">Verb</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr
                                    v-for="(item, index) in goodVerbenTaxo"
                                    :key="index"
                                  >
                                    <td>{{ item.stufe }}</td>
                                    <td>{{ item.verb }}</td>
                                  </tr>
                                </tbody>
                              </template>
                            </v-simple-table>
                          </v-expansion-panel-content>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-expansion-panels
              v-if="modalVerbRule"
              v-model="suggPanelsModalVerbs"
              focusable
              accordion
              multiple
              class="mb-5"
            >
              <v-expansion-panel v-for="(item, i) in modalVerbsOC" :key="i">
                <v-expansion-panel-header>
                  <v-row>
                    <v-col cols="12">
                      <v-chip
                        label
                        width="100%"
                        style="background-color: LightBlue"
                        >können <v-icon>mdi-arrow-right-thick</v-icon>
                        {{ item }}
                      </v-chip>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-card flat>
                    <v-card-text class="px-2">
                      <ul>
                        <li>
                          <b>"können"</b> ist in diesem Fall ein Modalverb und
                          bezieht sich in diesem Satz auf das Verb
                          <b>"{{ item }}"</b>.
                        </li>
                        <li>
                          Das <b>"Können"</b> einer Person ist im Bezug auf
                          <b>"{{ item }}"</b> nur schwer messbar.
                        </li>
                        <li>
                          Versuchen Sie <b>"können"</b> zu vermeiden, indem Sie
                          den Satz umstellen und es nicht als Hilfsverb
                          benutzen.
                        </li>
                        <li>
                          Das Hilfsverb <b>"können"</b>, welches den
                          Kompetenzaspekt anzeigt kann in den meisten Fällen
                          problemlos weggelassen werden. Es ist also ohne
                          weiteres möglich <b>"{{ item }}"</b> zu schreiben
                          statt <b>"können ... {{ item }}"</b>.
                        </li>
                        <li>
                          Gelegentlich führen Formulierungen ohne das Hilfsverb
                          <b>"können"</b> zu Missverständnissen und stören
                          Lesefluß oder verkomplizieren den Satzbau. In solchen
                          Fällen ist es zulässig das HIlfsverb zu nutzen.
                        </li>
                        <li>
                          Um etwaigen Missverständisse zu umgehen ist es
                          ratssam, den Satz so umzustellen, dass dieser das
                          HIlfsverb <b>"können"</b> nicht benötigt.
                        </li>
                      </ul>
                      <div class="ma-4">
                        Hier finden Sie ein Beispiel, wie sich ein solcher Satz
                        umstellen lässt:
                      </div>
                    </v-card-text>
                    <v-card-actions>
                      <v-btn
                        large
                        block
                        style="text-transform: unset"
                        color="blue-grey lighten-5"
                        @click="
                          dialogBsp = true
                          modalVerbInfo = true
                        "
                        >Beispiel</v-btn
                      >
                    </v-card-actions>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-expansion-panels
              v-if="unusedSentsRule"
              v-model="suggPanelsUnusedSents"
              focusable
              accordion
              multiple
              class="mb-5"
            >
              <v-expansion-panel v-for="(item, i) in noVerbsSents" :key="i">
                <v-expansion-panel-header>
                  <v-row>
                    <v-col cols="12">
                      <v-chip
                        label
                        width="100%"
                        style="background-color: yellow"
                        >entbehrlicher Satz
                        <v-col cols="3">
                          <v-avatar right size="32" color="blue-grey lighten-4">
                            {{ i + 1 }}
                          </v-avatar>
                        </v-col>
                      </v-chip>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-card flat>
                    <v-card-text class="px-2">
                      <ul>
                        <li>
                          Der Satz <b>"{{ item }}"</b> beinhaltet wahrscheinlich
                          keine passende Kompetenzbeschreibung.
                        </li>
                        <li>
                          Versuchen Sie in jedem Satz ein Kompetenzbeschreibung
                          einzubauen, basierend auf den empfohlenen Verben nach
                          den Taxonomiestufen von Bloom.
                        </li>
                      </ul>
                      <div class="ma-4">
                        Hier finden Sie eine Liste der empfholenen Verben und
                        ein Beispiel:
                      </div>
                      <v-expansion-panels>
                        <v-expansion-panel id="suggVerbsTable">
                          <v-expansion-panel-header color="blue-grey lighten-5"
                            >empfohlene Verben</v-expansion-panel-header
                          >
                          <v-expansion-panel-content style="padding: 0px">
                            <v-simple-table fixed-header height="350px" dense>
                              <template v-slot:default>
                                <thead>
                                  <tr>
                                    <th class="text-left">Taxonomiestufe</th>
                                    <th class="text-left">Verb</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr
                                    v-for="(item, index) in goodVerbenTaxo"
                                    :key="index"
                                  >
                                    <td>{{ item.stufe }}</td>
                                    <td>{{ item.verb }}</td>
                                  </tr>
                                </tbody>
                              </template>
                            </v-simple-table>
                          </v-expansion-panel-content>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                    <v-card-actions>
                      <v-btn
                        block
                        large
                        color="blue-grey lighten-5"
                        style="text-transform: unset"
                        @click="
                          dialogBsp = true
                          unusedSentsInfos = true
                        "
                        >Beispiel</v-btn
                      >
                    </v-card-actions>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-expansion-panels
              v-if="unsedVerbsNLPRule"
              v-model="suggPanelsunsedVerbsNLP"
              focusable
              accordion
              multiple
              class="mb-5"
            >
              <v-expansion-panel>
                <v-expansion-panel-header>
                  <v-row>
                    <v-col cols="12">
                      <v-chip
                        label
                        width="100%"
                        style="background-color: LightGrey"
                      >
                        neutrale Verben
                      </v-chip>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-card flat>
                    <v-card-text class="px-2">
                      <ul>
                        <li>
                          Verben wie <b>{{ unsedVerbsNLP[0] }}</b> wurden vom
                          Editor korrekt als Verb identifiziert.
                        </li>

                        <li>
                          Diese Verben werden als
                          <b>neutrale Verben</b> betrachtet da sie weder zu den
                          <b>empfohlenen Verben</b> noch zu den
                          <b>nicht empfohlenen Verb</b> gezählt werden.
                        </li>
                        <li>
                          Die Verwendung von <b>neutralen Verben</b> wird sich
                          nicht auf die Bewertung auswirken.
                        </li>
                      </ul>
                      <v-simple-table
                        fixed-header
                        height="150px"
                        dense
                        class="mt-4"
                      >
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th class="text-left">
                                neutrale Verben, die im Text vorkommen:
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="(item, index) in unsedVerbsNLP"
                              :key="index"
                            >
                              <td>{{ item }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                    </v-card-text>
                    <v-card-actions> </v-card-actions>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>
      </v-sheet>
    </v-col>
    <v-dialog v-model="dialogBsp" width="1000" persistent>
      <v-card tile>
        <v-card-title class="text-h5 grey lighten-2">
          Beispiel <v-spacer></v-spacer>
          <v-btn color="error" depressed fab small @click="closeDialog()">
            <v-icon>mdi-close</v-icon></v-btn
          ></v-card-title
        >
        <v-card-text>
          <div v-if="modalVerbInfo" class="pt-5">
            <v-row>
              <v-col cols="5" class="subtitle-1">
                <div class="font-weight-bold">nicht empfohlen:</div>
                Studierenden
                <span class="text-decoration-line-through">kennen</span>
                grundlegende Konzepte der Arbeit mit Kommandozeilen und
                <span class="text-decoration-line-through">können</span>
                diese für verschiedene Aufgaben benutzen.</v-col
              >
              <v-col cols="1" class="align-self-center"
                ><v-icon>mdi-arrow-right-thick</v-icon></v-col
              >
              <v-col cols="5" class="subtitle-1">
                <div class="font-weight-bold">empfohlen:</div>
                Die Studierenden
                <span class="text-decoration-underline">erinnern</span> sich an
                grundlegende Konzepte der Arbeit mit Kommandozeilen und
                <span class="text-decoration-underline">benutzen</span> diese
                für verschiedene Aufgaben.</v-col
              >
            </v-row>
          </div>
          <div v-if="unusedSentsInfos" class="pt-5">
            <v-row>
              <v-col cols="5" class="subtitle-1">
                <div class="font-weight-bold">nicht empfohlen:</div>
                Die Studierenden beherrschen den Umgang mit grundlegenden
                Begriffen und Methoden der Mathematik hinter der Computergrafik
                und können diese zur Lösung anwendungsbezogener Fragestellungen
                anwenden.
                <span style="background-color: yellow">
                  Das Modul findet in den Softwarelaboren statt.</span
                >
              </v-col>
              <v-col cols="1" class="align-self-center"
                ><v-icon>mdi-arrow-right-thick</v-icon></v-col
              >
              <v-col cols="5" class="subtitle-1">
                <div class="font-weight-bold">empfohlen:</div>
                Die Studierenden beherrschen den Umgang mit grundlegenden
                Begriffen und Methoden der Mathematik hinter der Computergrafik
                und können diese zur Lösung anwendungsbezogener Fragestellungen
                anwenden.
              </v-col>
            </v-row>
          </div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions> </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogInfo" width="1000" persistent>
      <v-card tile>
        <v-card-title class="text-h5 grey lighten-2">
          Information
          <v-spacer></v-spacer>
          <v-btn color="error" depressed fab small @click="closeDialog()">
            <v-icon>mdi-close</v-icon></v-btn
          >
        </v-card-title>
        <v-card-text>
          <div v-if="suggentionsInfo">
            <p class="title pt-5">Vorschläge</p>
            <p>
              In diesem Bereich werden Vorschläge und Informationen angezeigt.
            </p>
            <p>Diese beziehen sich auf den von Ihnen eingegebenen Text.</p>
            <p>
              Mit Hilfe einer Natural Language Processing (NLP) Software wird
              der Text ausgewertet und analysiert.
            </p>
            <p>
              Auf Basis dieser Analyse werden hier verschiedene dynamische Boxen
              angezeigt, die sich aufklappen lassen.
            </p>
            <p>
              Diese Boxen enthalten Vorschläge und INformationen, sowie
              Erläutertungen über die Analyse des Textes.
            </p>
            <p>
              Die Anzeige erfolgt annährend in Echtzeit. Sobald der Nutzer
              aufgehört hat zu tippen werden die Boxen eine Sekunde später
              aktualisiert.
            </p>
          </div>
          <div v-if="textareaInfo">
            <p class="title pt-5">Texteingabefeld</p>
            <p>Dies ist das Eingabefeld für Ihre Kompetenztbeschreibung.</p>
            <p>
              Hier können Sie einen Freitext mit der Tastatur eigeben oder einen
              bereits geschieben Text einfügen.
            </p>
            <p>
              Mit Hilfe einer Natural Language Processing (NLP) Software wird
              der Text ausgewertet und analysiert. Sobald keine Eingabe mehr
              registriert wird aktualisiert sich exakt eine Sekunde später die
              Ansicht und die Wörter werden entsprechend ihrer Gewichtung
              hervorgehoben.
            </p>
            <p>
              Auf dem <b>Speichern</b>-Button kann der aktuelle Text gespeichert
              werden und wird in der Übersicht angezeigt.
            </p>
            <div>
              <b
                ><v-chip label color="error" small
                  ><v-icon small left>mdi-alert</v-icon>ACHTUNG</v-chip
                >
              </b>
              <p>In dieser Beta-Version gibt es einige Einschränkungen:</p>
              <ul>
                <li>
                  Es kann zu Fehlern und unerwartetem Verhalten bei der
                  Hervorhgebung der entsprechenden Wörter kommen.
                </li>
                <li>
                  Es ist nicht empfohlen vorformatierten Text einzufügen, die
                  kann zu unerwarteten und fehlerhaftem Verhalten führen.
                </li>
              </ul>
            </div>
            <div class="mt-3">
              Bekannte Fehler/Bugs:
              <ul>
                <li>
                  Die "neutralen Verben" werden erst nach einer Eingabe
                  hervorgehoben
                </li>
                <li>
                  Es kann vorkommen, dass die Hervorhgebungen, der Wörter die an
                  letzter Stelle im Trexyt stehen nicht richtig erkannt werden,
                  nach erneuter Eingabe.
                </li>
                <li>
                  Die Hervorhgebung von Wörter mit ähnlichen Wortstamm, die
                  jeweils in anderen Kategorien eingeordnet sind, wie "erkennen"
                  und "kennen", kann zu fehlerhaften Hervorhebungen führen. Dies
                  ist rein optisch und die Bewertung wird trotzdessen korrekt
                  ausgeführt.
                </li>
              </ul>
            </div>
          </div>
          <div v-if="scoreInfo">
            <p class="title pt-5">Bewertung</p>
            <p>Alle Sätze ergeben zu gleichen Teilen die Gesamtbewertung</p>
            <p>
              Das bedeutedet, dass die Gesamtanzahl der Sätze 100% entspricht.
            </p>
            <p>
              Anteilig von diesen 100% werden die negativen Sätze, welche
              <b>nicht empfohlene Verben</b> abgezogen.
            </p>
            <p>
              Ähnlich wird mit den <b>entbehrlichen Sätzen</b> verfahren, mit
              dem Unterschied, dass diese Sätze jeweils nur zu 75% anteilg die
              Bewertung negativ beeinflussen.
            </p>
            <p>
              Mit dieser Formel wird die Bewertung ausgerechnet:
              <v-img
                src="img/forumla.png"
                max-width="950"
              ></v-img>
            </p>
          </div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions> </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogAction" width="500" persistent>
      <v-card tile>
        <v-card-title class="text-h5 grey lighten-2">
          Kompetenzbeschreibung speichern
        </v-card-title>
        <v-card-text class="mt-4">
          <v-row>
            <v-col cols="12" sm="12">
              Bitte geben Sie einen geeigenten Namen für Ihre
              Kompetenztbeschreibung an. Im Normafall ist der Name das Modul,
              für das die Kompentenzbeschreibung erstellt wurde.
            </v-col>
            <v-col cols="12" sm="12">
              <v-text-field
                v-model="compName"
                label="Name"
                placeholder="Name ggfs. Modul"
                outlined
                hide-details
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="error" @click="dialogAction = false"> abbrechen</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="success" @click="saveComp()"> speichern</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script>
import { db } from '../plugins/db'

export default {
  data: () => ({
    highlightEnabled: true,
    textareaPlaceholder:
      'Schreiben Sie hier Ihre kompetenzbeschreibungen, fügen Sie einen Text mit STRG+V ein oder wählen Sie aus der rechten Leiste eine bestehende Beschreibung aus...',
    text: '',
    highlightedText: '',
    typingDelay: 1000,
    timer: null,
    nlpSentencesLength: 0,
    nlpSentences: [],
    nlpVerbs: [],
    nlpNouns: [],
    nlpAdjectives: [],

    einleitungenWords: [],
    badVerben: [],
    badVerbsColor: '',
    uniqueBadVerbs: [],
    allTextBadVerbs: [],
    allTextGoodVerbs: [],
    goodVerben: [],
    goodVerbenTaxo: [],
    goodVerbsColor: '',
    uniqueGoodVerbs: [],
    noVerbsSents: [],
    noVerbsSentsScore: 0,
    badSentsScore: 0,
    unusedSents: [],
    unusedSentsRule: false,
    suggPanelsUnusedSents: [],
    modalVerbs: [],
    modalVerbsOC: [],
    uniqueModalVerbs: [],
    suggPanelsModalVerbs: [],
    suggPanelsModal: [],
    modalVerbRule: false,
    unsedVerbsNLP: [],
    suggPanelsunsedVerbsNLP: [],
    unsedVerbsNLPRule: false,
    einleitungenCount: 0,
    goodVerbsCount: 0,
    badVerbsCount: 0,
    highlight: [],
    dialogInfo: false,
    textareaInfo: false,
    unusedSentsInfos: false,
    modalVerbInfo: false,
    scoreInfo: false,
    suggentionsInfo: false,
    dialogAction: false,
    dialogBsp: false,
    compName: null,
    statusFinal: false,
    badVerbRule: false,
    suggPanels: [],
    compID: null,

    // score vars
    score: 0,
    spezVal: 0,
    perfVal: 0,
    domVal: 0,
    tempScore: 0,
    goodSentScore: 0,
    badSentScore: 0,

    editableShow: true,
    fakeOutput: false,
  }),
  created() {
    this.badVerbsColor = 'lightcoral'
    this.goodVerbsColor = 'lightgreen'
  },
  mounted() {
    this.compID = this.$store.getters.getCurrCompetenceID
    this.setCompetence()
    if (this.compName === null) {
      this.compName = 'Unbenannt'
    }
  },
  methods: {
    switchViews() {},
    foobar(val) {
      alert(val)
    },
    closeDialog() {
      // schließe Info-Dialog
      this.dialogInfo = false
      this.dialogBsp = false

      // setze alle Alternativen Dialoginfotext auf unsichtbar
      setTimeout(() => {
        this.textareaInfo = false
        this.modalVerbInfo = false
        this.unusedSentsInfos = false
        this.suggentionsInfo = false
        this.scoreInfo = false
      }, 500)
    },
    setCompetence() {
      this.fillHighlight()
      if (this.compID > 0) {
        db.kompetenzbeschreibungen
          .where('id')
          .equals(this.compID)
          .toArray((result) => {
            this.text = result[0].text
            this.compName = result[0].name
            return result[0].text
          })
          .then((text) => {
            this.processHighlighted(text)
          })
          .catch((err) => {
            console.error(err)
          })
      }
    },
    nlp(txt) {
      // remove html tags
      const txt2 = txt.replace(/(<([^>]+)>)/gi, '')
      // remove special chars that provenly cause errors
      const valTxt = txt2.replace(/([/])/g, ' ')

      const getDep = async () => {
        try {
          this.nlpVerbs = []
          this.nlpNouns = []
          this.nlpAdjectives = []
          this.modalVerbsOC = []
          const res = await this.$axios.post('/api/dep', {
            text: valTxt,
            model: 'de_core_news_sm',
          })
          const words = res.data.words
          const verbs = res.data.words
          const nouns = res.data.words
          const adjectives = res.data.words
          const labels = res.data.arcs

          labels.forEach((el) => {
            if (el.label === 'oc') {
              if (words[el.start].text === 'können') {
                this.modalVerbsOC.push(el.text)
              }
            }
          })
          verbs.forEach((el) => {
            if (el.tag.startsWith('V')) {
              this.nlpVerbs.push(el.text)
            }
          })
          nouns.forEach((el) => {
            if (el.tag.startsWith('N')) {
              this.nlpNouns.push(el.text)
            }
          })
          adjectives.forEach((el) => {
            if (el.tag.startsWith('ADJ')) {
              this.nlpAdjectives.push(el.text)
            }
          })
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
        this.suggPanelsModal = this.modalVerbsOC
        this.checkVerben()
        this.computeScore()
        this.showSuggestions()
      }
      const getSentsDep = async () => {
        try {
          this.noVerbsSents = []
          this.nlpSentences = []
          const res = await this.$axios.post('/api/sents_dep', {
            text: valTxt,
            model: 'de_core_news_sm',
          })

          res.data.forEach((el) => {
            if (!/^\s*$/.test(el.sentence)) {
              //  console.log("NO SPACE")
              this.noVerbsSents.push(el.sentence)

              this.nlpSentences.push(el.sentence)
            }
          })
          this.nlpSentencesLength = this.nlpSentences.length
        } catch (err) {
          // Handle Error Here
          console.error(err)
          console.error(err.request)
          console.error(err.message)
        }
      }
      getSentsDep()
      getDep()
    },
    processHighlighted(val) {
      this.nlp(this.text)
      let tempTxt = val
      this.highlight.forEach((el) => {
        // ##########################################
        // could be usefull for unused sentence to highlight
        // if (typeof el.sentence !== 'undefined') {
        //   const strRegExPatternSent = el.sentence
        //   const matchesSent = tempTxt.matchAll(
        //     new RegExp(strRegExPatternSent, 'g')
        //   )
        //   for (const m of matchesSent) {
        //     console.log(`${m} at ${m.index}`)
        //               tempTxt = tempTxt.replaceAll(
        //     m,
        //     '<mark style="' + el.style + '">' + m + '</mark>'
        //   )
        //   }
        // }
        // ##########################################
        const strRegExPattern = '\\b' + el.text + '\\b'
        const matches = tempTxt.matchAll(new RegExp(strRegExPattern, 'g'))

        for (const m of matches) {
          tempTxt = tempTxt.replaceAll(
            m,
            '<mark style="' + el.style + '">' + m + '</mark>'
          )
        }
      })
      this.highlightedText = tempTxt
    },
    checkVerben() {
      this.uniqueGoodVerbs = [...new Set(this.goodVerben)]
      this.goodVerbsCount = 0
      const uniqueGoodSents = []
      this.goodSentScore = 0
      this.allTextGoodVerbs = []
      this.unsedVerbsNLP = [...new Set(this.nlpVerbs)]

      this.nlpVerbs.forEach((nv) => {
        this.uniqueGoodVerbs.forEach((gv) => {
          if (nv === gv) {
            this.unsedVerbsNLP.forEach((el, i) => {
              if (el === nv || el === 'können') {
                this.unsedVerbsNLP.splice(i, 1)
              }
            })
            this.goodVerbsCount++
            this.allTextGoodVerbs.push(gv)
            this.nlpSentences.forEach((se) => {
              if (se.includes(gv) && !uniqueGoodSents.includes(se)) {
                uniqueGoodSents.push(se)
                this.goodSentScore += 1
                for (let i = 0; i < this.noVerbsSents.length; i++) {
                  if (this.noVerbsSents[i].includes(gv)) {
                    this.noVerbsSents.splice(i, 1)
                  }
                }
              }
            })
          }
        })
      })
      this.uniqueBadVerbs = [...new Set(this.badVerben)]
      this.badVerbsCount = 0
      const uniqueBadSents = []
      this.badSentScore = 0
      this.allTextBadVerbs = []
      this.nlpVerbs.forEach((nv) => {
        this.uniqueBadVerbs.forEach((bv) => {
          if (nv === bv) {
            this.unsedVerbsNLP.forEach((el, i) => {
              if (el === nv || el === 'können') {
                this.unsedVerbsNLP.splice(i, 1)
              }
            })
            this.badVerbsCount++
            this.allTextBadVerbs.push(bv)
            this.nlpSentences.forEach((se) => {
              if (se.includes(bv) && !uniqueBadSents.includes(se)) {
                uniqueBadSents.push(se)

                this.badSentScore += 1
                for (let i = 0; i < this.noVerbsSents.length; i++) {
                  if (this.noVerbsSents[i].includes(bv)) {
                    this.noVerbsSents.splice(i, 1)
                  }
                }
              }
            })
          }
        })
      })
      this.allTextBadVerbs = [...new Set(this.allTextBadVerbs)]
      this.fillHighlight()
      // ##########################################
      // could be usefull for unused sentence to highlight
      // this.noVerbsSents.forEach((item) => {
      //   this.highlight.push({
      //     sentence: item,
      //     style: 'background-color:yellow; color:yellow',
      //   })
      // })
      // ##########################################
    },
    fillHighlightAfterNLP() {
      this.unsedVerbsNLP.forEach((item) => {
        this.highlight.push({
          text: item,
          style: 'color:LightGrey; background-color:LightGrey',
        })
      })
    },
    fillHighlight() {
      this.highlight = []
      // entsprechende Einträge aus Tabelle holen und in Array pushen
      db.schlechteVerben
        .toArray((verbenArr) => {
          verbenArr.forEach((item) => {
            this.badVerben.push(item.verb)
          })
          this.uniqueBadVerbs = [...new Set(this.badVerben)]
          this.uniqueBadVerbs.forEach((item) => {
            this.highlight.push({
              text: item,
              style: 'background-color:lightcoral; color:lightcoral',
            })
          })
        })
        .then(
          db.verben.toArray((verbenArr) => {
            verbenArr.forEach((item) => {
              this.goodVerben.push(item.verb)
              this.goodVerbenTaxo.push(item)
            })
            this.uniqueGoodVerbs = [...new Set(this.goodVerben)]
            this.uniqueGoodVerbs.forEach((item) => {
              this.highlight.push({
                text: item,
                style: 'background-color:lightgreen; color:lightgreen',
              })
            })
          })
        )
        .then(
          db.modalVerben.toArray((verbenArr) => {
            verbenArr.forEach((item) => {
              this.modalVerbs.push(item.verb)
            })
            this.uniqueModalVerbs = [...new Set(this.modalVerbs)]
            this.uniqueModalVerbs.forEach((item) => {
              this.highlight.push({
                text: item,
                style: 'background-color:LightBlue; color:LightBlue',
              })
            })
          })
        )
        .then(() => {
          this.fillHighlightAfterNLP()
        })
        .catch((err) => {
          console.error(err)
        })
    },
    showSuggestions() {
      if (this.badVerbsCount > 0) {
        this.suggPanels = [0]
        this.badVerbRule = true
      } else {
        this.badVerbRule = false
      }

      if (this.modalVerbsOC.length > 0) {
        this.modalVerbRule = true
      } else {
        this.modalVerbRule = false
      }

      if (this.noVerbsSents.length > 0) {
        this.unusedSentsRule = true
      } else {
        this.unusedSentsRule = false
      }

      if (this.unsedVerbsNLP.length > 0) {
        this.unsedVerbsNLPRule = true
      } else {
        this.unsedVerbsNLPRule = false
      }
      this.suggPanelsModal = []
    },
    computeScore() {
      const divider = 100 / this.nlpSentencesLength
      const badSents = divider * this.badSentScore
      this.badSentsScore = badSents
      const noSents = divider * this.noVerbsSents.length
      this.noVerbsSentsScore = noSents * 0.75
      const final = 100 + (-(noSents * 0.75) - badSents)

      this.score = (Math.round((final + Number.EPSILON) * 100) / 100).toFixed(2)
      this.badSentsScore = Number(this.badSentsScore).toFixed(2)
      this.noVerbsSentsScore = Number(this.noVerbsSentsScore).toFixed(2)

      if (this.score > 100) {
        this.score = 100
      } else if (this.score < 0) {
        this.score = 0
      } else if (isNaN(this.score)) {
        this.score = 0
      }
    },
    saveComp() {
      this.dialogAction = false
      const today = new Date()
      const date =
        today.getDate() +
        '.' +
        (today.getMonth() + 1) +
        '.' +
        today.getFullYear()
      db.kompetenzbeschreibungen
        .add({
          name: this.compName,
          text: this.text,
          saetze: this.nlpSentences.length,
          wertung: this.score,
          datum: date,
          datumUnix: Math.floor(today.getTime() / 1000),
        })
        .then((resID) => {
          this.$store.commit('setLastSavedCompetenceID', resID)
        })
    },
  },
}
</script>
<style scoped>
#textBox:focus {
  outline: 2px solid #1976d2;
  border-color: #1976d2;
}
#fakeOutput {
  height: calc(70vh - 158px);
  overflow-y: auto;
  padding: 15px;
  font-size: 16px;
  color: red;
  position: absolute;
  top: 4vh;
}
[contenteditable='true']:empty:before {
  content: attr(placeholder);
  pointer-events: none;
  color: grey;
  display: block;
}
.thickBorderCard {
  border-width: 2px !important;
}

#suggVerbsTable
  .v-expansion-panel-content
  >>> .v-expansion-panel-content__wrap {
  padding: 0px !important;
}
.v-list-item__content {
  padding: 0% !important;
}
</style>