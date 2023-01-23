'''
File containing all application strings.
'''

from config import OBS_REC_TIME as RT

# UI strings/text.
STRINGS = {

    "NOR": {
        "select-scene":     "Velg en bakgrunn:",
        "exit-button-pg2":  "AVBRYT",
        "cont-button-pg2":  "FORTSETT TIL OPPTAK",

        "mail-header":      "Skriv inn din e-post addresse:",
        "mail-hint":        "brukernavn@mail.no",
        "mail-info":        f"Opptaket blir sendt til den angitte adressen.\nSendingen varer i {RT} sekunder.",
        "exit-button-pg3":  "TILBAKE",
        "cont-button-pg3":  "START OPPTAK",

        "recording":        "OPPTAK PÅGÅR",

        "sending":          "SENDER OPPTAKET",

        "mail-subject":     "Din film fra Nordnorsk vitensenter",
        "mail-body":        "Her er værreportasjen du spilte inn på Nordnorsk vitensenter.",
        "recording-sent":   "OPPTAK SENDT",
        "sending-failed":   "SENDING FEILET"
    },

    "ENG": {
        "select-scene":     "Select a background:",
        "exit-button-pg2":  "CANCEL",
        "cont-button-pg2":  "CONTINUE TO RECORDING",

        "mail-header":      "Enter your e-mail address:",
        "mail-hint":        "username@mail.com",
        "mail-info":        f"The recording will be sent to the given address.\nThe broadcast lasts for {RT} seconds.",
        "exit-button-pg3":  "RETURN",
        "cont-button-pg3":  "START RECORDING",

        "recording":        "RECORDING IN PROGRESS",

        "sending":          "SENDING THE RECORDING",

        "mail-subject":     "Your film from the Science Centre of Northern Norway",
        "mail-body":        "Here is the weather report you recorded at the Science Centre of Northern Norway.",
        "recording-sent":   "RECORDING SENT",
        "sending-failed":   "FAILED TO SEND"
    },

    "GER": {
        "select-scene":     "Wählen Sie einen Hintergrund:",
        "exit-button-pg2":  "ABBRECHEN",
        "cont-button-pg2":  "MIT AUFZEICHNUNG FORTFAHREN",

        "mail-header":      "Geben Sie Ihre E-Mail-Adresse ein:",
        "mail-hint":        "benutzername@mail.com",
        "mail-info":        f"Die Aufzeichnung wird an die angegebene Adresse gesendet.\nDie Übertragung dauert {RT} Sekunden.",
        "exit-button-pg3":  "ZURÜCK",
        "cont-button-pg3":  "AUFNAHME BEGINNEN",

        "recording":        "AUFNAHME LAUFT",

        "sending":          "AUFZEICHNUNG WIRD GESENDET",

        "mail-subject":     "Ihr Film vom Wissenschaftszentrum Nordnorwegen",
        "mail-body":        "Hier ist der Wetterbericht, den Sie im Wissenschaftszentrum Nordnorwegens aufgezeichnet haben.",
        "recording-sent":   "AUFZEICHNUNG GESENDET",
        "sending-failed":   "SENDEN FEHLGESCHLAGEN"
    }
}

# UI window title.
UI_TITLE = "Weather Report Station"

# String printed in console when OBS is not responding.
OBS_CONN_ERROR = "OBS connection error: OBS not responding!"

if __name__ == "__main__":
    ''' Run simple demo. '''

    print(STRINGS["NOR"]["mail-info"])