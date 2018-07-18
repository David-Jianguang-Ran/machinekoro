import React from "react"

// this app is used to send json to the server during development

const TextField = function (props) {
    return(
        <div id={"fake_console"} >
            <ul>
                {props.displayTxt.map(function (row,index) {
                    return <li key={ index }>{row}</li>
                })}
            </ul>
        </div>

    )}

class TestApp extends React.Component{
    constructor(props){
        super(props)
        this.messageList = ["initial line"]
        //this.componentDidMount = this.componentDidMount.bind(this)// is this already done for me?
        this.receiveMessage = this.receiveMessage.bind(this)
        this.sendMessage = this.sendMessage.bind(this)
        this.addToMsgList = this.addToMsgList.bind(this)
        this.state = {
            messageSerial: 0
        }
    }
    componentDidMount(){
        // and event listener for incoming message over ws connection
        this.props.wsManager.addMessageListener('default',this.receiveMessage)
    }
    addToMsgList(msg,local=true){
        let entry = null
        if (local){
            entry = "\nClient Message :" + msg
        } else {
            entry = "\nServer Message :" + msg
        }
        this.messageList.push(entry)
    }
    receiveMessage(msg){
        // in this function, implement a switch/ type checker if ws messages needs to be routed
        // multiple components
        console.log("message routed to component")
        this.addToMsgList(msg.content,false)
        this.setState({
            messageSerial: this.state.messageSerial + 1
        })
    }
    sendMessage(){
        // don't forget to stringyfy json
        const msgContent = document.getElementById("message").value
        let message = {
            "type":"client.message",
            "content":msgContent
        }
        this.props.wsManager.sendJSON(message)
        this.addToMsgList(msgContent)
        console.log("message sent")
        // return false // to stop the page from refreshing
    }
    render(){
        return(
            <div>
                <TextField displayTxt={this.messageList}/>
                <textarea id={"message"} rows={10} cols={30}>
                        Enter Commands Here
                </textarea>
                <button id={"go_button"} onClick={this.sendMessage}>Send Message</button>
            </div>
        )
    }}

export default TestApp