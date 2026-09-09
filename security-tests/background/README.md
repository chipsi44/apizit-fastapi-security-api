# Tâche ASGI après body

## Objectif et abus représenté

Profiter du délai entre l'envoi du body et la fin de la tâche ASGI. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /background` — 1 tâche de 200 ms par appel ; 2 requêtes actives maximum.

```text
curl -X POST http://127.0.0.1:8080/background
```

## Observation attendue sur APIZIT

Comparer /state, fin ASGI, durée Lambda et réponse publique ; TestClient peut attendre la tâche.

## Protection à vérifier et réaction idéale

Comptabilité de l'invocation complète. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

