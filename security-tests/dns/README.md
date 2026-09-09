# DNS localhost

## Objectif et abus représenté

Vérifier la disponibilité du résolveur sans viser de système tiers. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /dns` — 1 résolution de localhost, attente 1 s ; aucun hostname fourni par le client.

```text
curl -X GET http://127.0.0.1:8080/dns
```

## Observation attendue sur APIZIT

Observer nombre de résultats ; ne conclure ni sur Internet ni sur les réseaux privés.

## Protection à vérifier et réaction idéale

Politique réseau à qualifier ultérieurement sur cible dédiée. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
