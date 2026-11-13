# CurseForge-Upload einrichten

Der GitHub-Workflow **Publish to CurseForge** baut und testet die Version eines veröffentlichten GitHub-Releases und lädt das Addon anschließend zu [Forever Frost Alert auf CurseForge](https://www.curseforge.com/wow/addons/forever-frost-alert) hoch. Projekt-ID und WoW-Version sind bereits hinterlegt: **1796931**, **Forever 1.60.1**.

Du musst einmalig deinen persönlichen **CurseForge-Autoren-API-Token** als GitHub-Secret speichern. Ein Schlüssel für die separate CurseForge Core API ist hierfür nicht geeignet.

## 1. Token bei CurseForge erzeugen

1. Melde dich im [CurseForge-Autorenportal](https://authors.curseforge.com/) mit dem Account an, der Forever Frost Alert verwalten darf.
2. Öffne **API Tokens**. Den direkten Link findest du auch unter **Generate a Token** in der [offiziellen Upload-API-Anleitung](https://support.curseforge.com/support/solutions/articles/9000197321-curseforge-upload-api#Generate-a-Token).
3. Erzeuge einen neuen Token, beispielsweise mit dem Namen **Forever Frost Alert GitHub**.
4. Kopiere den erzeugten Token für den nächsten Schritt.

Der Token gehört ausschließlich in das GitHub-Secret. Füge ihn nicht in den Quellcode, eine Anleitung, ein Issue oder einen Chat ein.

## 2. Token als GitHub-Secret speichern

1. Öffne direkt die [Actions-Secrets dieses Repositorys](https://github.com/1nd1v1d/Forever_Frost_Alert/settings/secrets/actions).
2. Der Menüpfad ist **Einstellungen → Geheimnisse und Variablen → Aktionen** beziehungsweise **Settings → Secrets and variables → Actions**.
3. Klicke auf **Neues Repository-Geheimnis / New repository secret**. Verwende ein **Repository secret**, keine normale Actions-Variable.
4. Trage diese beiden Felder ein:

   | Feld | Inhalt |
   | --- | --- |
   | Name | `CF_API_TOKEN` |
   | Secret / Geheimnis | Dein gerade erzeugter CurseForge-Token |

5. Speichere mit **Geheimnis hinzufügen / Add secret**.

Der Name muss genau `CF_API_TOKEN` lauten. Der Workflow liest den Wert automatisch; weitere Änderungen an den Dateien sind nicht erforderlich. Die [GitHub-Dokumentation zu Actions-Secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) beschreibt denselben Ablauf.

## 3. Vorhandene Version 0.3.0 zunächst ohne Upload prüfen

Ein bereits veröffentlichtes Release startet nach dem Hinzufügen des Workflows oder Secrets nicht rückwirkend. Für Version 0.3.0 gibt es deshalb einen manuellen Start:

1. Öffne [Actions → Publish to CurseForge](https://github.com/1nd1v1d/Forever_Frost_Alert/actions/workflows/publish-curseforge.yml).
2. Klicke auf **Workflow ausführen / Run workflow**.
3. Wähle Branch **main** und trage bei **release_tag** den Wert `v0.3.0` ein.
4. Lasse **Validate and test only; do not upload to CurseForge** aktiviert (`dry_run = true`).
5. Starte den Workflow und öffne den neuen Lauf. Der letzte Prüfschritt muss melden: **Dry run complete. No CurseForge request was sent; no token is required.**

Dieser Probelauf führt die Tests aus und prüft das Paket. Er funktioniert auch vor dem Hinterlegen des Tokens und sendet keine Anfrage an CurseForge.

## 4. Die vorhandene Version tatsächlich hochladen

Prüfe zuerst im CurseForge-Autorenportal, ob **0.3.0 bereits manuell hochgeladen** wurde. Falls ja, lade diese Version nicht noch einmal hoch und nutze die Automatik erst für die nächste neue Version. Manuelle frühere Uploads erkennt der Workflow nicht automatisch.

Wenn die Version noch fehlt und das Secret hinterlegt ist, starte denselben Workflow erneut mit **main**, `release_tag = v0.3.0` und **deaktiviertem** Probelauf (`dry_run = false`).

Bei Erfolg zeigt das Protokoll **Upload accepted: CurseForge file …**. Am GitHub-Release wird zusätzlich die Datei **curseforge-upload.json** angehängt. Sie enthält die CurseForge-Datei-ID und den Paket-Fingerabdruck, keinen Token. Bei einem erneuten Start verhindert diese Quittung den doppelten Upload desselben Pakets.

## 5. Künftige Releases automatisch veröffentlichen

1. Aktualisiere die Addon-Version in TOC und Lua-Status sowie die Versionsangaben in `docs/publication/project-metadata.json`. Aktualisiere außerdem README, Changelog und Release Notes. Tag, TOC und Metadaten müssen dieselbe Version angeben.
2. Baue und teste das Addon entsprechend dem [Publishing Guide](UPLOAD_GUIDE.md). Committe und pushe die Änderungen.
3. Erstelle für diesen Commit ein GitHub-Release mit passendem Tag, beispielsweise `v0.3.1`, und hänge das installierbare Addon-ZIP und seine Prüfsumme an.
4. Veröffentliche das Release über GitHub oder einen mit deinem Benutzerkonto authentifizierten `gh release create`-Aufruf.

**Beim Veröffentlichen** startet der Workflow automatisch:

- GitHub **Pre-release** → CurseForge **Beta**.
- Normales GitHub-Release → CurseForge **Release**.
- Ein gespeicherter Entwurf oder ein reiner Tag-Push löst keinen Upload aus.
- Ein mit dem internen `GITHUB_TOKEN` eines anderen Workflows erstelltes Release löst diesen Folge-Workflow nicht automatisch aus. Dafür müsste die Release-Automatik gesondert angepasst werden.

Der Workflow erstellt das Paket erneut aus dem Release-Tag, testet es und verwendet den GitHub-Release-Text als Datei-Changelog. Ist der Text leer, verwendet er `docs/publication/RELEASE_NOTES.md` aus dem Tag. Auf CurseForge wird die Spielversion **1.60.1** gesetzt. Die Freigabe kann anschließend noch von der CurseForge-Moderation abhängen.

Die allgemeine **Projektbeschreibung, das Logo und die Kategorien** werden durch diesen Datei-Upload nicht aktualisiert. Dafür bleibt der Autorenbereich zuständig; die englische Beschreibung steht in `CURSEFORGE_DESCRIPTION.md`.

## Wenn ein Lauf fehlschlägt

- **Missing CF_API_TOKEN:** Prüfe den exakten Secret-Namen und ob du es als Repository-Secret unter Actions hinterlegt hast.
- **HTTP 401 / 403:** Prüfe Token und Projektberechtigung. Erzeuge bei Bedarf einen neuen Autoren-Token und aktualisiere das vorhandene Secret.
- **Versionsfehler:** Tag, TOC und Metadaten müssen zusammenpassen. Ändere bereits veröffentlichte Tags nicht nachträglich; korrigiere eine neue Version.
- **Upload result is unknown**, ein Timeout oder ein Fehler beim Speichern der Quittung: Prüfe vor einem neuen Upload zuerst die CurseForge-Dateiliste. Die Datei könnte bereits angekommen sein. Der Workflow wiederholt den POST nicht automatisch.
- **Already uploaded … skipping duplicate upload:** Für diesen Tag und Paketinhalt liegt bereits eine gültige Quittung vor; es wird keine weitere Datei angelegt.

Zum Austauschen des Tokens öffnest du wieder die [Actions-Secrets](https://github.com/1nd1v1d/Forever_Frost_Alert/settings/secrets/actions) und bearbeitest **CF_API_TOKEN**. Der Wert wird nach dem Speichern nicht mehr angezeigt. Einen nicht mehr benötigten alten Token kannst du im CurseForge-Autorenportal widerrufen.

## Sprache des Addons

Menü und Chatmeldungen richten sich automatisch nach der im WoW-Client gewählten Sprache (`GetLocale()`). **Deutsch (`deDE`)** und **Englisch (`enUS`/`enGB`)** sind enthalten. Für andere Clientsprachen wird Englisch verwendet. Die Sprache des GitHub- oder CurseForge-Kontos verändert die Addon-Sprache nicht. Nach einem Wechsel der Client-Sprache lade die Benutzeroberfläche mit `/reload` neu beziehungsweise starte den Client nach dessen Sprachwechsel neu.
