GDPC                                                                                         P   res://.godot/exported/133200997/export-a8e1520d83f25710dd4e3da8c6f32601-Main.scnP      O      OD����Q��_���        res://.godot/extension_list.cfg �8      5       q�Y��C�)�$    ,   res://.godot/global_script_class_cache.cfg  01      �      ���[��a]=����:�    D   res://.godot/imported/icon.svg-218a8f2b3041327d8a5756f3a245f83b.ctex#      �      �̛�*$q�*�́        res://.godot/uid_cache.bin  �7            -�>��Y�.(.�    $   res://Data/CardsServer.1.translation�      R      o���0�SIq҈y��    $   res://Data/CardsServer.csv.import   �      R       ..����a��=\@I:       res://Scenes/Main.tscn.remap�0      a       �u��.]�V����       res://Scripts/Connector.gd  �            kB�E�����Dk�Bb        res://Scripts/Data/CardObject.gdp      2      Vұ�!Bd��҂��	        res://Scripts/Data/DeckObject.gd�      �      �_�h��:ܹ�YM        res://Scripts/Data/HandObject.gd�      z      �3Oi7N}]Kz�I�W�    $   res://Scripts/Data/PlayerObject.gd  0      �       'H�`|g���lm�]�    $   res://Scripts/Data/UserConnection.gd�      �      �3{�,Eh������r3       res://Scripts/Server.gd �             �b>ޓ7I=�4��n    4   res://addons/godot-git-plugin/git_plugin.gdextension        �      k��$f�0o�`r�b       res://icon.svg  �3      �      C��=U���^Qu��U3       res://icon.svg.import   �/      �       oT��^�fXWg%��&       res://project.binary 9      �      $�م�"2sd�G<��            [configuration]

entry_symbol = "git_plugin_init"
compatibility_minimum = "4.1.0"

[libraries]

macos.editor = "macos/libgit_plugin.macos.editor.universal.dylib"
windows.editor.x86_64 = "win64/libgit_plugin.windows.editor.x86_64.dll"
linux.editor.x86_64 = "linux/libgit_plugin.linux.editor.x86_64.so"
linux.editor.arm64 = "linux/libgit_plugin.linux.editor.arm64.so"
linux.editor.rv64 = ""
           [remap]

importer="csv_translation"
type="Translation"
uid="uid://c1oinibt6o2vy"
               RSRC                    OptimizedTranslation            �$嵐m3                                                   resource_local_to_scene    resource_name 	   messages    locale    hash_table    bucket_table    strings    script        #   local://OptimizedTranslation_phflv )         OptimizedTranslation          RSRC              RSRC                    PackedScene            ��������                                                  resource_local_to_scene    resource_name    line_spacing    font 
   font_size    font_color    outline_size    outline_color    shadow_size    shadow_color    shadow_offset    script 	   _bundled           local://LabelSettings_mtjf4 �         local://PackedScene_wyn4v �         LabelSettings          �            PackedScene          	         names "         Main    layout_mode    anchors_preset    anchor_right    anchor_bottom    grow_horizontal    grow_vertical    size_flags_horizontal    Control    Label    anchor_left    anchor_top    offset_left    offset_top    offset_right    offset_bottom    text    label_settings    	   variants                        �?                              ?    �F�     ��    �FC     �B      Server                 node_count             nodes     8   ��������       ����                                                          	   	   ����               
                                 	      
                                           conn_count              conns               node_paths              editable_instances              version             RSRC 
class_name DeckObject

var cards : Array = []

signal beforeDraw(card : CardObject)
signal afterDraw(card : CardObject)

signal beforeRemove(card : CardObject)
signal afterRemove(card : CardObject)

signal beforeShuffle(cards : Array)
signal afterShuffle(cards : Array)

signal beforeReset(cards : Array, graveyard : Array)
signal afterReset(cards : Array, graveyard : Array)

func draw(hand : HandData) -> void:
	var cardToDraw = null
	if cards.size() > 0:
		cardToDraw = cards.pop_front()
	emit_signal("beforeDraw", cardToDraw)
	hand.addCard(cardToDraw)
	emit_signal("afterDraw")

func removeCard(cardData : CardObject):
	var index : int = cards.find(cardData)
	if index != -1:
		removeAt(index)

func removeAt(index : int):
	if index >= 0 and index < cards.size():
		var cardToRemove : CardObject = cards[index]
		emit_signal("beforeRemove", cardToRemove)
		cards.erase(cardToRemove)
		emit_signal("afterRemove", cardToRemove)

func shuffle() -> void:
	emit_signal("beforeShuffle", cards)
	cards.shuffle()
	emit_signal("afterShuffle", cards)

func reset(graveyard : Array):
	emit_signal("beforeReset", cards, graveyard)
	cards += graveyard
	graveyard.clear()
	shuffle()
	emit_signal("afterReset", cards, graveyard)
             
class_name CardObject

var uuid : int = -1

var name : String = "_NONE"

var power : int = -1
var toughness : int = -1
var damage : int = 0

var abilities : Array = []

var owner : PlayerObject = null
var controller : PlayerObject = null

var node = null

enum ZONES {NONE, DECK, HAND, GRAVEYARD, TERRITORY, QUEUE, FUSED}
var zone : int = ZONES.NONE

func _init(uuid : int, name : String, power : int, toughness : int, abilities : Array):
	self.uuid = uuid
	self.name = name
	self.power = power
	self.toughness = toughness
	self.abilities = abilities

func setOwner(owner : PlayerObject) -> void:
	self.owner = owner

func setController(controller : PlayerObject) -> void:
	self.controller = controller

func setDamage(damage : int) -> void:
	self.damage = damage

func setZone(zone : int) -> void:
	self.zone = zone
              
class_name HandObject

var player : PlayerObject = null
var cards : Array = []

signal beforeAdd(cardData : CardObject)
signal afterAdd(cardData : CardObject)

signal beforeRemove(cardData : CardObject)
signal afterRemove(cardData : CardObject)

func _init(player : PlayerObject):
	self.player = player

func addCard(cardData : CardObject):
	pass

func removeCard(card):
	pass
      
class_name PlayerObject

var playerID : int = -1
var color : Color = Color(1.0, 0.0, 1.0, 1.0)

func _init(playerID : int, color : Color):
	self.playerID = playerID
	self.color = color
      
class_name UserConnection

var ip : String = ""
var port : int = -1

func _init(ip : String = "", port : int = -1):
	self.ip = ip
	self.port = port

func matches(ip : String, port : int) -> bool:
	return self.ip == ip# and self.port == port

func _to_string():
	return ip + ":" + str(port)

static func strip(data : String) -> UserConnection:
	var split : Array = data.split(':')
	if split.size() != 2:
		return null
	return UserConnection.new(split[0], int(split[1]))
          extends Node

func _init():
	var args : Array = OS.get_cmdline_args()
	var i : int = 0
	while i < args.size():
		var arg : String = args[i]
		if i < args.size() - 1:
			if arg == "-p":
				i += 1
				if (args[i] as String).is_valid_int():
					Server.port = int(args[i])
			elif arg == "-c":
				i += 1
				var userCon : UserConnection = UserConnection.strip(args[i])
				if userCon != null:
					Server.waitingFor.append(userCon)
		i += 1
	
	Server.numPlayers = Server.waitingFor.size()
	
	print("Waiting for users: ")
	for user in Server.waitingFor:
		print("  >  ", user)

func _ready():
	Server.connect("onPlayerConnect", self.onPlayerConnect)
	Server.connect("onPlayerDisconnect", self.onPlayerDisconnect)

func onPlayerConnect(playerID : int):
	var playerIP : String = Server.serverPeer.get_peer(playerID).get_remote_address()
	var playerPort : int = Server.serverPeer.get_peer(playerID).get_remote_port()
	
	if not playerID in Server.connectedPlayers.keys():
		for i in range(Server.waitingFor.size()):
			if Server.waitingFor[i].matches(playerIP, playerPort):
				Server.waitingFor.remove_at(i)
				Server.connectedPlayers[playerID] = [playerIP, playerPort]
				print("ACCEPTED: User(" + playerIP + ":" + str(playerPort) + ")")
				if Server.waitingFor.size() == 0:
					print("Starting Match!")
					Server.isAllConnected = true
				return
	else:
		for userCon in Server.disconnectTimer.keys():
			if userCon.matches(playerIP, playerPort):
				Server.disconnectTimer.erase(userCon)
				print("RECONNECT: User(" + playerIP + ":" + str(playerPort) + ")")
				return
		
	print("REJECTED: User(" + playerIP + ":" + str(playerPort) + ")")
	Server.serverPeer.disconnect_peer(playerID, true)

func onPlayerDisconnect(playerID : int):
	if playerID in Server.connectedPlayers.keys():
		var playerIP : String = Server.connectedPlayers[playerID][0]
		var playerPort : int = Server.connectedPlayers[playerID][1]
		Server.disconnectTimer[UserConnection.new(playerIP, playerPort)] = Server.DISCONNECT_MAX_TIME
		print("User(" + playerIP + ":" + str(playerPort) + ") disconnected.")

  extends Node

var waitingFor : Array = []
var serverPeer : ENetMultiplayerPeer = null
var port : int = -1
var numPlayers : int = -1
var isAllConnected : bool = false

const CONNECT_MAX_TIME : float = 16.0
var connectTimer : float = CONNECT_MAX_TIME

const DISCONNECT_MAX_TIME : float = 60.0
var disconnectTimer : Dictionary = {}

var connectedPlayers : Dictionary = {}

signal onPlayerConnect(playerID : int)
signal onPlayerDisconnect(playerID : int)

func _ready():
	if port == -1:
		print("ERROR: Could not start game. No port given")
		get_tree().quit()
		return
	elif numPlayers == -1:
		print("ERROR: Could not start game. No player count given")
		get_tree().quit()
		return
	
	serverPeer = ENetMultiplayerPeer.new()
	serverPeer.create_server(port, numPlayers + 1)
	multiplayer.multiplayer_peer = serverPeer
	serverPeer.connect("peer_connected", self.onPeerConnected)
	serverPeer.connect("peer_disconnected", self.onPeerDisconnected)

func onPeerConnected(id : int):
	emit_signal("onPlayerConnect", id)

func onPeerDisconnected(id : int):
	emit_signal("onPlayerDisconnect", id)

func _process(delta):
	if not isAllConnected:
		connectTimer -= delta
		if connectTimer <= 0:
			print("ERROR: Could not establish connection with all users!")
			endMatch()
	else:
		for user in disconnectTimer.keys():
			disconnectTimer[user] -= delta
			if disconnectTimer[user] <= 0:
				print("ERROR: User could not reconnect")
				endMatch()

func endMatch() -> void:
	for id in connectedPlayers.keys():
		serverPeer.disconnect_peer(id, true)
	get_tree().quit()

               GST2   �   �      ����               � �        �  RIFF�  WEBPVP8L�  /������!"2�H�$�n윦���z�x����դ�<����q����F��Z��?&,
ScI_L �;����In#Y��0�p~��Z��m[��N����R,��#"� )���d��mG�������ڶ�$�ʹ���۶�=���mϬm۶mc�9��z��T��7�m+�}�����v��ح�m�m������$$P�����එ#���=�]��SnA�VhE��*JG�
&����^x��&�+���2ε�L2�@��		��S�2A�/E���d"?���Dh�+Z�@:�Gk�FbWd�\�C�Ӷg�g�k��Vo��<c{��4�;M�,5��ٜ2�Ζ�yO�S����qZ0��s���r?I��ѷE{�4�Ζ�i� xK�U��F�Z�y�SL�)���旵�V[�-�1Z�-�1���z�Q�>�tH�0��:[RGň6�=KVv�X�6�L;�N\���J���/0u���_��U��]���ǫ)�9��������!�&�?W�VfY�2���༏��2kSi����1!��z+�F�j=�R�O�{�
ۇ�P-�������\����y;�[ ���lm�F2K�ޱ|��S��d)é�r�BTZ)e�� ��֩A�2�����X�X'�e1߬���p��-�-f�E�ˊU	^�����T�ZT�m�*a|	׫�:V���G�r+�/�T��@U�N׼�h�+	*�*sN1e�,e���nbJL<����"g=O��AL�WO!��߈Q���,ɉ'���lzJ���Q����t��9�F���A��g�B-����G�f|��x��5�'+��O��y��������F��2�����R�q�):VtI���/ʎ�UfěĲr'�g�g����5�t�ۛ�F���S�j1p�)�JD̻�ZR���Pq�r/jt�/sO�C�u����i�y�K�(Q��7őA�2���R�ͥ+lgzJ~��,eA��.���k�eQ�,l'Ɨ�2�,eaS��S�ԟe)��x��ood�d)����h��ZZ��`z�պ��;�Cr�rpi&��՜�Pf��+���:w��b�DUeZ��ڡ��iA>IN>���܋�b�O<�A���)�R�4��8+��k�Jpey��.���7ryc�!��M�a���v_��/�����'��t5`=��~	`�����p\�u����*>:|ٻ@�G�����wƝ�����K5�NZal������LH�]I'�^���+@q(�q2q+�g�}�o�����S߈:�R�݉C������?�1�.��
�ڈL�Fb%ħA ����Q���2�͍J]_�� A��Fb�����ݏ�4o��'2��F�  ڹ���W�L |����YK5�-�E�n�K�|�ɭvD=��p!V3gS��`�p|r�l	F�4�1{�V'&����|pj� ߫'ş�pdT�7`&�
�1g�����@D�˅ �x?)~83+	p �3W�w��j"�� '�J��CM�+ �Ĝ��"���4� ����nΟ	�0C���q'�&5.��z@�S1l5Z��]�~L�L"�"�VS��8w.����H�B|���K(�}
r%Vk$f�����8�ڹ���R�dϝx/@�_�k'�8���E���r��D���K�z3�^���Vw��ZEl%~�Vc���R� �Xk[�3��B��Ğ�Y��A`_��fa��D{������ @ ��dg�������Mƚ�R�`���s����>x=�����	`��s���H���/ū�R�U�g�r���/����n�;�SSup`�S��6��u���⟦;Z�AN3�|�oh�9f�Pg�����^��g�t����x��)Oq�Q�My55jF����t9����,�z�Z�����2��#�)���"�u���}'�*�>�����ǯ[����82һ�n���0�<v�ݑa}.+n��'����W:4TY�����P�ר���Cȫۿ�Ϗ��?����Ӣ�K�|y�@suyo�<�����{��x}~�����~�AN]�q�9ޝ�GG�����[�L}~�`�f%4�R!1�no���������v!�G����Qw��m���"F!9�vٿü�|j�����*��{Ew[Á��������u.+�<���awͮ�ӓ�Q �:�Vd�5*��p�ioaE��,�LjP��	a�/�˰!{g:���3`=`]�2��y`�"��N�N�p���� ��3�Z��䏔��9"�ʞ l�zP�G�ߙj��V�>���n�/��׷�G��[���\��T��Ͷh���ag?1��O��6{s{����!�1�Y�����91Qry��=����y=�ٮh;�����[�tDV5�chȃ��v�G ��T/'XX���~Q�7��+[�e��Ti@j��)��9��J�hJV�#�jk�A�1�^6���=<ԧg�B�*o�߯.��/�>W[M���I�o?V���s��|yu�xt��]�].��Yyx�w���`��C���pH��tu�w�J��#Ef�Y݆v�f5�e��8��=�٢�e��W��M9J�u�}]釧7k���:�o�����Ç����ս�r3W���7k���e�������ϛk��Ϳ�_��lu�۹�g�w��~�ߗ�/��ݩ�-�->�I�͒���A�	���ߥζ,�}�3�UbY?�Ӓ�7q�Db����>~8�]
� ^n׹�[�o���Z-�ǫ�N;U���E4=eȢ�vk��Z�Y�j���k�j1�/eȢK��J�9|�,UX65]W����lQ-�"`�C�.~8ek�{Xy���d��<��Gf�ō�E�Ӗ�T� �g��Y�*��.͊e��"�]�d������h��ڠ����c�qV�ǷN��6�z���kD�6�L;�N\���Y�����
�O�ʨ1*]a�SN�=	fH�JN�9%'�S<C:��:`�s��~��jKEU�#i����$�K�TQD���G0H�=�� �d�-Q�H�4�5��L�r?����}��B+��,Q�yO�H�jD�4d�����0*�]�	~�ӎ�.�"����%
��d$"5zxA:�U��H���H%jس{���kW��)�	8J��v�}�rK�F�@�t)FXu����G'.X�8�KH;���[             [remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://cdbkoikl38p6o"
path="res://.godot/imported/icon.svg-218a8f2b3041327d8a5756f3a245f83b.ctex"
metadata={
"vram_texture": false
}
                [remap]

path="res://.godot/exported/133200997/export-a8e1520d83f25710dd4e3da8c6f32601-Main.scn"
               list=Array[Dictionary]([{
"base": &"RefCounted",
"class": &"CardObject",
"icon": "",
"language": &"GDScript",
"path": "res://Scripts/Data/CardObject.gd"
}, {
"base": &"RefCounted",
"class": &"DeckObject",
"icon": "",
"language": &"GDScript",
"path": "res://Scripts/Data/DeckObject.gd"
}, {
"base": &"RefCounted",
"class": &"HandObject",
"icon": "",
"language": &"GDScript",
"path": "res://Scripts/Data/HandObject.gd"
}, {
"base": &"RefCounted",
"class": &"PlayerObject",
"icon": "",
"language": &"GDScript",
"path": "res://Scripts/Data/PlayerObject.gd"
}, {
"base": &"RefCounted",
"class": &"UserConnection",
"icon": "",
"language": &"GDScript",
"path": "res://Scripts/Data/UserConnection.gd"
}])
       <svg height="128" width="128" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="2" width="124" height="124" rx="14" fill="#363d52" stroke="#212532" stroke-width="4"/><g transform="scale(.101) translate(122 122)"><g fill="#fff"><path d="M105 673v33q407 354 814 0v-33z"/><path fill="#478cbf" d="m105 673 152 14q12 1 15 14l4 67 132 10 8-61q2-11 15-15h162q13 4 15 15l8 61 132-10 4-67q3-13 15-14l152-14V427q30-39 56-81-35-59-83-108-43 20-82 47-40-37-88-64 7-51 8-102-59-28-123-42-26 43-46 89-49-7-98 0-20-46-46-89-64 14-123 42 1 51 8 102-48 27-88 64-39-27-82-47-48 49-83 108 26 42 56 81zm0 33v39c0 276 813 276 813 0v-39l-134 12-5 69q-2 10-14 13l-162 11q-12 0-16-11l-10-65H447l-10 65q-4 11-16 11l-162-11q-12-3-14-13l-5-69z"/><path d="M483 600c3 34 55 34 58 0v-86c-3-34-55-34-58 0z"/><circle cx="725" cy="526" r="90"/><circle cx="299" cy="526" r="90"/></g><g fill="#414042"><circle cx="307" cy="532" r="60"/><circle cx="717" cy="532" r="60"/></g></g></svg>
             'L�32E   res://icon.svg4�4�(GI   res://Main.tscn4�4�(GI   res://Scenes/Main.tscnA��L~   res://Scenes/Main.tscnFoɠ�,q$   res://Data/CardsServer.1.translation���Ʊh�[   res://Data/CardsServer.csv�$嵐m3 $   res://Data/CardsServer.1.translation             res://addons/godot-git-plugin/git_plugin.gdextension
           ECFG      application/config/name         FusionServer   application/run/main_scene          res://Scenes/Main.tscn     application/config/features$   "         4.2    Forward Plus       application/config/icon         res://icon.svg     autoload/Server          *res://Scripts/Server.gd   autoload/Connector$         *res://Scripts/Connector.gd "   editor/version_control/plugin_name      	   GitPlugin   *   editor/version_control/autoload_on_startup                 