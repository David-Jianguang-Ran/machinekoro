import {MdPanTool} from "react-icons/md"
import React from "react"

import EmoFace from "./emoFace"
import emojis from "./emojis.json"
import faces from "./faces.json"

class SomePlayerLobby extends React.Component{
    /*
    This component is a emoface display and also a button to kick a player
    props:
            is_prime (the client)
            player
            kickPlayerCallBack
    */
    constructor(props){
        super(props)
        this.handleKickCmd = this.handleKickCmd.bind(this)
    }
    handleKickCmd(event){
        // fires callback to kick player
        this.props.kickPlayerCallBack(this.props.player)
    }
    render(){
        let face_img = faces[this.props.player.face].icon
        let emoji_img = emojis[this.props.player.emoji].icon
        if (this.props.is_prime === true){
            // prime player has the ability to kick other players
            return (
                <div className={"some_lobby_player"}>
                    <EmoFace face={face_img} emoji={emoji_img}/>
                    <div>
                        <MdPanTool onClick={this.handleKickCmd}/>
                        <h6>Kick Player</h6>
                    </div>
                </div>
            )
        } else {
            return (
                <div className={"some_lobby_player"}>
                    <EmoFace face={face_img} emoji={emoji_img}/>
                </div>
            )
        }
    }
}

export default SomePlayerLobby