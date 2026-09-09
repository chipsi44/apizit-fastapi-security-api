# Codes applicatifs ambigus

## Objectif et abus représenté

Faire ressembler une erreur client à un refus d'abonnement ou de capacité. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /codes` — Liste fixe : 200,400,402,403,404,409,429,500,503.

```text
curl -X GET http://127.0.0.1:8080/codes
```

## Observation attendue sur APIZIT

Comparer origin=customer_fixture avec erreurs réellement produites par APIZIT.

## Protection à vérifier et réaction idéale

Projection fidèle des erreurs sans accorder d'entitlements. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
