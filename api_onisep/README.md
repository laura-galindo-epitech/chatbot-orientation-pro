# Utilisation de l'API d'Onisep

https://opendata.onisep.fr/3-api.htm

## Obtention de la clé API (validité 24h)

1) Se créer un compte sur https://opendata.onisep.fr/

2) Exécuter la commande :

```
curl -X POST -d email=(your-e-mail) -d password=(your-password) "https://api.opendata.onisep.fr/api/1.0/login"
```

Voici un exemple de token obtenu :

```
{"token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXUyJ9.eyJleHAiOjE3MzgzMjQxOTAsInVzZXJuYW1lIjoibGF1cmEuZ2FsaW5kb0BlcGl0ZWNoLmRpZ2l0YWwiLCJpYXQiOiIxNzM4MjM3NzkwIn0.NBWhMg-q71BnDJTBapqYIkpggqr2GezVIQa1QxzOAjbLh-JBw0J09dC0QbzG0DY459pV-KKgNiFaN8pX97e77EMQCbrN19OfwxKo3NX7gRvkppUVOnIUitOggFS66wgHIVxOdqrJUPuvF5ZK6zZnNHjODXJ1nXCODeZnoCzCxqld1kqmC1tYEiJsNWtzgh9H7_nQ4niUFOdmyEbSDQ2R8FSP0iBl1MGS2vrGHfoxHgTGAub4DSq0-lqf1iFfxDCWN8AAKHXwwARMICOv-0zDX76YxspFB8-z4V0Kyk58HQ0DSL8HszfwF6dW3srPIkCSI-BOU2vEcSaPpzsesuUjnIcm0s5cscENNmuZlqWFJuMA3qvTnxHKg6njmQ4UisYpv-r1JVPY7TUzIm33rvRX1xWsOlOW-WxQU_1nJR1mrIhChveZRnIWIh0l6w-1rfDk5YasRH956znWtLDhYUE7AZoTzIci--hFDT2pqcCegNMASQrwf1DWNywjZ4iMQj9qbWJL1DHOjLDUTI4EboRQjy0AkWyYB7FoT5ISelVauPUpiG4YZAlfNCe3uHtDW0qae0_8CDZGkZZ_IoxZCJe8w8kTFc9FC7pJiQ1Eu5pVWahXg1dmkPTnwwUwhrEO-JecdR2tWYg96BJiCZ0k2-7qdvn5PJaFAPxUIckJvWMQKrQ"}
```