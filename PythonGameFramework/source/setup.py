from sound import MusicPlayer, SoundEffectPlayer, SoundWrapper
from player_character import PlayerCharacter
from actions import ActionColorSwap, ActionMove
from actors import SimpleBox
from event import EventHandler
import parameters as PRAM

# Generates the sound and music players, and loads the entire soundtrack into
#     the dictionaries of each
def soundPlayerFactory():
    musicPlayer = MusicPlayer()
    soundPlayer = SoundEffectPlayer()
    for song in PRAM.MUSIC_PLAYLIST:
        musicPlayer.loadSong(SoundWrapper('song', PRAM.MUSIC_PATH, song, '.mp3'))
    for sound in PRAM.SOUNDEFFECTS:
        soundPlayer.loadSound(SoundWrapper('sound', PRAM.SOUND_PATH, sound, '.wav'))
    for ambience in PRAM.AMBIANCE:
        soundPlayer.loadSound(SoundWrapper('sound', PRAM.AMBIANCE_PATH, ambience, '.wav'))        
    return musicPlayer, soundPlayer

# Initialize the player character and create the starting actions.  May not start
# with an actor initialized
# @param actor
def playerFactory(actor=None):
    player = PlayerCharacter(actor)
    player.actor=SimpleBox()
    player.actor.isFocus = True
    actionMove = ActionMove(player)
    defaultAction = ActionColorSwap(player)
    player.actionMove=actionMove.act
    player.defaultAction=defaultAction.act
    return player

    
def eventHandlerFactory(game):
    eventHandler = EventHandler(game, {})
    eventHandler.eventDict.update({
     'MOVE' : eventHandler.runMove,
     'DEFAULTACTION' : eventHandler.runDefaultAction,
     'NOTIFYMOVE' : eventHandler.runNotifyMove,
     'SOUND' : eventHandler.runSound,
     'SONG' : eventHandler.runSong,
     'SETINPUT' : eventHandler.runSetInput,
     'LOADLEVEL' : eventHandler.runLoadLevel,
     'LOADMENU' : eventHandler.runLoadMenu,  
     'LOADCUTSCENE' : eventHandler.runLoadCutscene,    
     })
    
    return eventHandler   
    
