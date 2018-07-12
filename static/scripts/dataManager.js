// this module handles the communicating with the server over websocket connection and
// store some data in memory here as attributes
// and exposes the state attributes to other scripts


// WebSocketManager data can be called in react components by this.props.wsManager.dataStore.listName
export class WebSocketManager {
    constructor(room_serial){
        const ws_url = string.concat("ws://127.0.0.1:8000/ws/live/",room_serial);
        let dStore = {
            playerNum:null,
            lobbyWorldState:null,
            inGameWorldState:null,
            querylist:null,
        };
        this.webSocketConnection = new WebSocket(ws_url);
        this.webSocketConnection.addEventListener('message',this.messageProcessor());
        this.dataStore = dStore;
        console.log(string.concat("ws manager instance start",room_serial));
    }
    // parse incoming message and save to corresponding listened variables
    messageProcessor (text_data) {
        if (text_data.c_type == 'client.init') {
            // saves player_num to memory on receiving message
            this.dataStore.playerNum = text_data.playerNum
        } else if (text_data.c_type == 'lobby_update') {
            this.dataStore.lobbyWorldState = text_data.content
        } else if (text_data.c_type == 'world_update') {
            this.dataStore.inGameWorldState = text_data.content
        } else if (text_data.c_type == 'action.query') {
            this.dataStore.querylist.push(text_data)
        }
    }

    // send obj as json over ws
    sendMessage (message) {
        let text_data = JSON.stringify(message)
        console.log("message sent over ws")
    }
}

export default WebSocketManager


