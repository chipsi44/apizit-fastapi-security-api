# Streaming borné

## Objectif et abus représenté

Maintenir une réponse ouverte en produisant progressivement des données. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /stream` — 32 fragments de 4 KiB ; attente totale programmée 320 ms.

```text
curl -X GET http://127.0.0.1:8080/stream
```

## Observation attendue sur APIZIT

Comparer premier octet local/public ; l'adaptateur peut bufferiser le flux.

## Protection à vérifier et réaction idéale

Deadline, buffering et finalisation. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

