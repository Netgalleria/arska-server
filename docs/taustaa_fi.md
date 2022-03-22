# Powerguru - energian kulutuksen ja varastoinnin ohjausjärjestelmä

**Sähköturvallisuudesta
Vain valtuutettu sähköalan ammattilainen saa tehdä verkkovirtaan kytkettyjen laitteiden , kuten myöhemmin mainittujen energiamittareiden ja varaajien ohjaamiseen käytettyjen verkkovirtareleiden asennutöitä. Hän on myös vastuussa asennustöiden verkkovirtalaitteiden asennusten turvallisuudesta. JÄTÄ VERKKOVIRTALAITTEIDEN VALINNAT JA KYTKENNÄT AINA AMMATTILAISELLE!**

## Yleistä
Arska on energian kulutuksen ja varastoinnin ohjausjärjestelmä on tarkoitettu optimoimaan kiinteistön (aurinkovoimalan) sähköntuotannon käyttöä sekä sähkön hankintaa edullisimmille tunneille. Automaattisen ohjauksen mahdollistamiseksi kiinteistössä on oltava yksi tai useampi energiavarasto, johon energiaa voidaan varastoida myöhempää käyttöä varten. Tyypillisesti energiaa voidaa varastoida lämpönä esim. vesivaraajiin tai rakenteisiin lattialämmityksen avulla tai sähköauton akkuun tai kiinteään kotiakkuun. 

Ohjelmiston ensimmäinen versio on ollut käytössä vuoden 2020 kesästä alkaen ohjaamassa eteläsuomalaisen maatilan 30 kWp aurinkovoimalan tuotannon käyttöä. Tämän version kehitetty versio 2 otetaan testikäyttöön kevättalvella 2022. Ohjelmiston lähdekoodi ja perusohjeistus on vapaasti saatavilla [Githubissa](https://powerguru.eu). Arska Node sovellus toimii ESP8266-mikrokontrollerille, johon kytketään tarvittavat lisälaitteet tietojen lukemiseksi ja laitteiden ohjaamiseksi. Lisäksi Arska Server palvelulta saadaan

## Ominaisuudet
Sovelluksen tärkeimmät ominaisuudet lyhyesti
- Oman (aurinkovoimalan) tuotannon fiksu ohjaus ensisijaisesti omaan käyttöön tai myyntiin kalliin energian aikana.
- Sähkön oston ajoittaminen edullisimmille tunneille erityisesti, jos käytössä on pörssisähkö (tai yösähkö).
- Tuntitinetotuksen ja vuonna 2023 käyttöönotettavan varttinetotuksen hyödyntäminen.

### Oman käytön maksimointi ja myynnin ajoitus

Itse tuotetun sähkön oma käyttö maksimoidaan (aurinkopaneeleilla)  varaamalla lämpöä vesivaarajiin tai rakenteisiin (lattialämmitys) ja vähennetään näin ostoenergian tarvetta. Ostoenergiasta joutuu maksamaan aina verkkoyhtiölle verkkopalvelumaksun (siirtomaksu), joten oman käytön maksimointi on yleensä hyvin kannattavaa. Mikäli sähkön hintapiikki osuus aurinkoiselle tunnille on Arskan avulla mahdollista omaa kulutusta (esim. varaajaan)  tällöin rajoittaa ja myydä mahdollisimman paljon verkkoon. Tämä voi olla kannattavaa mikäli "korvaava" sähkö on myöhemmin saatavissa omista aurinkopaneeleista tai ostettavissa selkeästi halvemmalla (verkkopalvelumaksu huomioiden).

### Ostettavan energian kulutuksen ohjaus
Kun omaa tuotantoa ei ole saatavissa (kun aurinko ei paista) voidaan energian ostoa kohdistaa edullisimmille tunneille. Tämä riippuu valitusta sähköenergian ostosopimuksesta (pörssisähkö, kiinteä, yö/päivä jne) sekä verkkopalvelusopimuksen tyypistä. Sähkön ollessa edullisinta se on yleisesti myös puhtaimmin tuotettua, joten edullisiin tunteihin ostojen painottaminen on myös ekoteko. 

Pörssisähköä käytettäessä järjestelmänn sääntöjen avulla voidaan ohjata kulutusta edullisimmille tunneilla. Kellonaikaan tai kalenteriin sidotulla sopimuksella sähköä ostavien on mahdollista määritellä ohjeusehdot vastaavasti. Ehdoissa voidaan määritellä esim. tavoitetason varaajan lämpötilalle tai varaaja voidaan pitää päällä vain edullisimman sähkön aikana, jolloin se on toimii optimoidummin kuin pelkästään ajastimella käynnistettävä varaaja.

### Tuntinetotuksen hyödyntäminen 
Arska tukee sähköverkon tuntinetotusta ja  myöhemmin käyttöönotettavaa 15-minuutin netotusta. Käytännössä tämä tarkoittaa sitä, että kun on omaa tuotantoa (aurinko paistaa) niin osto ja myynti pyritään tasapainottomaan kyseisen ajan (60 tai 15 minuuttia)  sisällä esim. varaajia ohjaamalla. Esimerkiksi jos aurinkovoimala tuottaa tunnin aikana tasaisen 2kW:n "ylimääräisen" tehon (joka menisi muuten myyntiin), niin Arska kytkee 6 kW-tehoisen varaajan päälle tunnin aikana yhteensä 20 minuutiksi. Tällöin kyseisen tunnin ajalla laskennallisesti sähkön osto ja myynti ovat tasapainossa, eikä ostosta (eikä siirrosta) laskuteta eikä myynnistä makseta, vaikka tunnin aikana sähköä onkin kulkenut verkosta/verkkoon. Lisätieto tuntinetotuksesta https://yle.fi/uutiset/3-11767604 


### Energiasääennuste
Arska osaa hyödyntää paikkakunnalle laadittua energiasääennustetta. Esimerkiksi jos ennusteessa on luvattu tulevalle päivällä korkeaa aurinkovoimalan tuottoa voidaan varaajien tai lattialämmityksen lämmitystä siirtää päivään lämmittämällä yöllä minimitasolle ja mahdollistamalla näin itsetuotetulle sähkölle käyttökohde päivällä. Mikäli tulossa onkin pimeä päivä (vähän omaa tuotantoa), niin lämmitys kannattaa tehdä halvemmalla yösähköllä tai tyypillisesti halvemmila spot-hinnoilla.



Arska Nodeen kytketyltä releeltä saadaan ns. kärkitieto, jolla voidaan ohjata kärkitietoa hyödyntäviä lämpöpumppuja tai esim. vesikiertoista lattialämmitystä. Tietyissä Ouman-lämmönsäätimissä on kotona/poissa-kytkin, joka voidaan myös liittää automaattiseen ohjaukseen. Näin lämpöä varataan betonilaattaan kytkemällä ohjain kotona-tilaan  (korkeampi lämpötila) kun energia edullista ja lämmitystä vastaavasti vähennetään kytkemällä Ouman poissa-tilaan. Käyttäjä voi säätää Oumaniin em. tilojen lämpötilat halutuiksi - mitä suurempi lämpötilaero sitä enemmän voidaan lämpöä tarvittaessa varastoida lattiarakenteeseen. 


### Tietolähteet
Ohjelmisto kerää tietoa tarpeen mukaan valituista tietolähteistä. Tietolähteitä voivat olla:
- sähköliittymän kokonaiskulutusta/-myyntiä mittavaa ns. takamittari
- aurinkovoimalan invertterin tuotantotiedot
- sähkön nykyiset ja tulevat spot-hinnat
- aurinkovoimalan lähiajan tuotantoa ennustava energiasääennuste
- vesivaraajien lämpötila-anturit
- sähköauton tai akuston varaustieto (suunnitteilla)
![Data flow diagram](https://github.com/Olli69/powerguru/blob/main/docs/img/Powerguru%20data%20diagram.drawio.png?raw=true)

Sähkön markkinahinnat päivitetään eurooppalaisten verkko-operaattoreiden ylläpitämästä ENTSO-E -palvelusta https://www.entsoe.eu/.

### Takamittarointi
Laitteiden, esimerkiksi vesivaraajien, voi perustua aurinkovoimalan invertteriltä tulevaan tietoon senhetkisestä tuotetusta tehosta. Tällöin vesivaraaja voidaan kytkeä päälle, kun aurinkovoimalan tuotto ylittää asetetun rajan. Tämä voi olla riittävä tapa ohjata, jos kulutus on tasaista. Jos esim. oletetaan että talouden pohjakuorma aurinkoisena aikana on 2 kW, niin tämän ylittävä teho voidaan ohjata lämminvesivaraajalle, sillä muuten se menisi myyntiin (ja todennäköisesti myöhemmin varaajan lämmittämiseen ostettavan energian kokonaiskustannus olisi korkeampi). Arska tukee tätäkin ohjaustapaa, mikäli invertteri tukee tehotiedon automaattista hakua. Tarkempaan optimointiin päästään kuitenkin mikäli reaaliaikainen sähkönkulutus/myyntitieto luetaan ns. takamittarilta, jonka kautta kulkee kaikki sähköliittymän energia. Takamittari mittaa  samaa sähkövirtaa kuin verkkoyhtiön mittari, mutta se mahdollistaa tietojen reaaliaikaisen luvun järjestelmään - sähköyhtiön mittarilta ei reaaliaikaista tietoa ole saatavissa.

### Invertterin tiedot
Tällä hetkelle on kehitteillä liitännät tietyiltä Froniuksen ja SMA:n invertterimalleilta.

## Tekninen toteutus
Yksityiskohtaisempaa tietoa teknisestä toteutuksesta on luettavissa [englannikielisestä dokumentaatiosta](../README.md). 



### Telegraf
Tietojen keräämiseen ja [Telegraf](https://github.com/influxdata/telegraf)

### Tiedon analysointi - InfluxDB ja Grafana 
Järjestelmän keräämät tiedot voidaan tallentaa analysointia varten. Helpoimmin tietojen keruu ja analysointi onnistuu pilvipohjaisessa palvelussa, mutta tiedot on myös mahdollista kerätä omalla palvelimelle.




