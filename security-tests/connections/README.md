# Connexions locales

## Objectif et abus représenté

Multiplier les connexions HTTP depuis une requête. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /connections` — Désactivé par défaut ; 4 GET localhost:8766, timeout 300 ms, deadline 1 s.

```text
curl -X GET http://127.0.0.1:8080/connections
```

## Observation attendue sur APIZIT

Démarrer tools/peer.py localement ; compter les headers témoins, sans lire les bodies.

## Protection à vérifier et réaction idéale

Timeouts et connexions ; aucune qualification d'egress cloud. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

Local uniquement : lancer `python tools/peer.py`, puis démarrer l'API avec
`ADVERSARIAL_LOOPBACK_PEER=1`. Le peer écoute seulement `127.0.0.1:8766`, traite au
plus 100 cycles avec timeout et ne crée aucune ressource cloud. Les redirects et
proxies sont désactivés. Aucune URL, aucun header d'authentification et aucun body
du client ne sont transmis. Le peer local n'est pas un service hébergé APIZIT.
