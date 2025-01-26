This repository is for Amukan Sang Koboi, a game created for our Machine Vision course as part of our Mechatronics Engineering degree.
Our group members are: Tashfin Muqtasid, Ahmad Faiz Najmi bin Ahmad Fairus, and Tengku Muhammad Afnan Faliq bin Tuan Farezuddeen Ahmad

The objective of the game is to shoot an enemy cowboy on the screen, using your hand shaped in a gun gesture.
At the same time, the enemy cowboy will try to aim for your head as well.
Both the cowboy and the player have 5 life points, and the last one to survive will win.

The files included are:
1. hand_detector.py - A code that detects the gun gesture and allows the testing of the shooting function
2. BulletGameUI.py - A code that shows the user interface of our game, with all the assets we used
3. EnemyPopUp.py - A code that shows the enemy moving around the screen and aiming and shooting at the user
4. ASK.py - Our complete game code, with the integration of our functions and game logic
5. ASK_game.py - Our game code, combined with the start screen GUI

All the assets used in our game are inside the ASK file, which include audio tracks and images

## HOW TO PLAY ##
Launch ASK_game.py to start playing.
Press the Start button to start the game.
The game starts immediately, choose either hand to aim at the enemy cowboy and form your hand into a gun gesture.
The gun gesture requires your index finger to be straight, while the middle, ring and pinky finger must be completely bent.
A "Gun Detected" text will show and lines will be displayed on your hand, showing that the gun gesture has been detected.
Once the gun pose is detected, you can shoot at the enemy cowboy by bending your index finger, just like pulling the trigger of a gun.
The gun sound will play and you will lose one of your bullets.
You start with 5 bullets, and can reload by flicking your wrist inward (towards your forearm or away from the camera)
You must hit the enemy cowboy inside of your aim reticule for your shot to hit.
Once the enemy is hit, a hit sound will play and they will lose one lifepoint.
If you eliminate all their lifepoints, then you win.
However your head is your hitbox, if the enemy's aim reticule is inside your head region and they shoot, you will lose a lifepoint.
If you lose all your lifepoints then you will lose.
Upon either winning or losing, the game will end and either a "You Win" or "You Lose" message will be displayed.
To quit the game at any time, you can press `q` on your keyboard.


