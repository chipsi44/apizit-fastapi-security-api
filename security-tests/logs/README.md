# Logs synthétiques

## Objectif et abus représenté

Amplifier le volume et imiter des lignes de télémétrie applicative. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /logs` — 16 lignes fixes, aucun contenu de requête.

```text
curl -X POST http://127.0.0.1:8080/logs
```

## Observation attendue sur APIZIT

Observer volumes et séparation des logs client des sources autoritaires de métrologie.

## Protection à vérifier et réaction idéale

Limites et confiance dans la source des logs. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
