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
    updateFaceCallback(){
        // fill in message once back end has been updated
    }
    updateEmojiCallback(){
        // fill in message once back end has been updated
    }
    handlePrimeCmd(cmd){
        let message = {
            "key":"prime.player.command",
            "cmd":"cmd"
        }
        this.props.ws_manager.sendJSON(message)
    }
    render(){
        if (this.props.context.is_prime === true){
            return(
                <div>
                    <EmojiChooser updateEmojiCallback={this.updateEmojiCallback}/>
                    <FaceChooser updateFaceCallback={this.updateFaceCallback}/>
                    <MdAddToQueue onClick={this.handlePrimeCmd("add_bot")}/>
                    <MdPlayCircleOutline onClick={this.handlePrimeCmd("start_game")}/>
                </div>
            )
        } else {
            return (
                <div>
                    <EmojiChooser updateEmojiCallback={this.updateEmojiCallback}/>
                    <FaceChooser updateFaceCallback={this.updateFaceCallback}/>

                </div>
            )
        }
    }
}

export default LobbyUtilityBar