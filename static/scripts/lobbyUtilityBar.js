import {MdPlayCircleOutline, MdAddToQueue} from "react-icons/md"
import React from "react"

import EmojiChooser from "./emojiChooser"
import FaceChooser from "./faceChooser"


class LobbyUtilityBar extends React.Component{
    /*
    This component handles the messaging

    props:
    - ws_manager
    - context (register obj)
    - is_prime

    child components:
    - face chooser <expandable buttons>
    - emoji choose <expandable buttons>

    */
    constructor(props){
        super(props)
        this.updateEmojiCallback = this.updateEmojiCallback.bind(this)
        this.updateFaceCallback = this.updateFaceCallback.bind(this)
        this.handlePrimeCmd = this.handlePrimeCmd.bind(this)
    }
    updateFaceCallback(face_name){
        // fill in message once back end has been updated
        let message = {
            "key":"face.update",
            "face":face_name
        }
        this.props.ws_manager.sendJSON(message)
    }
    updateEmojiCallback(emoji_name){
        // fill in message once back end has been updated
        let message = {
            "key":"face.update",
            "emoji":emoji_name
        }
        this.props.ws_manager.sendJSON(message)
    }
    handlePrimeCmd(cmd){
        let message = {
            "key":"prime.player.command",
            "cmd":cmd
        }
        this.props.ws_manager.sendJSON(message)
    }
    render(){
        if (this.props.is_prime === true){
            return(
                <div className={"utility_bar"}>
                    <EmojiChooser updateEmojiCallback={this.updateEmojiCallback} className={"utility_button"}/>
                    <FaceChooser updateFaceCallback={this.updateFaceCallback} className={"utility_button"}/>
                    <MdAddToQueue onClick={() => (this.handlePrimeCmd("add_bot"))} className={"utility_button"}/>
                    <MdPlayCircleOutline onClick={() => (this.handlePrimeCmd("add_bot"))} className={"utility_button"}/>
                </div>
            )
        } else {
            return (
                <div className={"utility_bar"}>
                    <EmojiChooser updateEmojiCallback={this.updateEmojiCallback} className={"utility_button"}/>
                    <FaceChooser updateFaceCallback={this.updateFaceCallback} className={"utility_button"}/>
                </div>
            )
        }
    }
}

export default LobbyUtilityBar