@startuml
!include <C4/C4_Container>

title Tigers Coaching – Container Diagramm

Person(coach, "Coach", "Benutzt die Plattform zur Spielvorbereitung")
Person(admin, "Admin", "Verwaltet Benutzer und Inhalte")

System_Boundary(tc, "Tigers Coaching") {
  Container(user, "User", "React", "Benutzeroberfläche für Coaches und Admins")
  Container(agenda, "Agenda", "Flask", "Liefert und verwaltet Traininseinheit")
  Container(analyse, "Analyse", "Spiel- und Systemanalyse", "Liefert LLM Antworten")

  ContainerDb(agendadb, "Agenda Datenbank", "SQLite3", "Speichert Trainingsdaten")
}

System_Ext(llm, "AI Interface", "Externe Quelle für analysen")

Rel(coach, user, "Benutzt")
Rel(admin, user, "Benutzt")

Rel(user, agenda, "zeigt")
Rel(agenda, agendadb, "nutzt")

Rel(user, analyse,"zeigt")

Rel(analyse, llm, "nutzt")
@enduml