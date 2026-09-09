# Récursion HTTP simulée

## Objectif et abus représenté

Représenter une chaîne d'appels auto-récursifs ou inter-API. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /recursion` — 3 niveaux, 3 GET vers un peer ASGI en mémoire.

```text
curl -X GET http://127.0.0.1:8080/recursion
```

## Observation attendue sur APIZIT

Observer calls=3 ; aucun DNS, gateway, autre compte ou réseau réellement traversé.

## Protection à vérifier et réaction idéale

Futur budget des appels inter-API et prévention d'amplification. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

