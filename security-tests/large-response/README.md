# Réponse volumineuse

## Objectif et abus représenté

Consommer mémoire, sérialisation et bande passante par un simple GET. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /response` — 1 MiB fixe de données synthétiques.

```text
curl -X GET http://127.0.0.1:8080/response
```

## Observation attendue sur APIZIT

Observer taille publique, erreurs de transport et coût ; sous les limites cloud habituelles.

## Protection à vérifier et réaction idéale

Budget de réponse et comportement de l'adaptateur. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
