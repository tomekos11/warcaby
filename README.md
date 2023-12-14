# warcaby

Wymagane paczki:<br>
Django==3.2.23 (for MVC webServer)<br>
django-filter==2.2.0 (for filtering - optional)<br>
channels==4.0.0 (for webSocket)<br>
daphne==4.0.0 (for webSocket)<br><br>

opencv-python==4.8.1.78 (for computer vision scripts)


możliwe zasady gry:
1. wymuszane / niewymuszane bicie, gdy mamy możliwość
2. bicie zwykłym pionkiem do tyłu / brak bicia do tyłu zwykłym pionkiem
3. królówka po ubiciu pionka zatrzymuje się na pierwszym wolnym polu / może iść dalej
4. królówka maks 1 pole ruchu / królowka nieograniczony ruch


-2 = czarna królówka<br>
-1 = czarny pion<br>
0 = brak pionka na polu<br>
1 = biały pion<br>
2 = biała królówka<br>
