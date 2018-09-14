class WebSocketManager {
    // this obj is to be init and passed to the top level component as a prop in entry point
    // any child component can call this.prop.wsManager.sendJSON to send data
    // for an component to receive data, it must:
    // 1) write method used to handle incoming message in the class based component
    // 2) in component did mount or constructor (I haven't decided/tested constructor)
    // call addMessageListener with the string key and the message handler (don't call it with ())
    constructor(url) {
        this.messageRoutingTable = {
            "alert":alert
        }
        this.sendJSON = this.sendJSON.bind(this)
        this.messageSwitcher = this.messageSwitcher.bind(this)
        this.addMessageListener = this.addMessageListener.bind(this)
        this.ws = new WebSocket(url)
        this.ws.addEventListener('message', this.messageSwitcher)
        this.ws.addEventListener('onClose', () => (console.log(event)))
    }
    sendJSON(obj) {
        let data = JSON.stringify(obj)
        this.ws.send(data)
    }
    messageSwitcher(event) {
        let obj = JSON.parse(event.data)
        for (let key in this.messageRoutingTable) {
            if (key == obj.key) {
                this.messageRoutingTable[key](obj)
            }
        }
        console.log("message recieved following message has been received")
        console.log(obj)
    }
    addMessageListener(key, method) {
        this.messageRoutingTable[key] = method
        console.log("ws message listener added wit key" + key)
        console.log(this.messageRoutingTable)
    }
}

export default WebSocketManager

