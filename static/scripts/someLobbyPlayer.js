import React from "react"

import EmoFace from "./emoFace"

class SomeLobbyPlayer extends React.Component{
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
        if (this.props.is_prime === true){
            return (
                <div className={"some_lobby_player"}>
                    <EmoFace player={this.props.player}/>
                    <button onClick={this.handleKickCmd}>Kick</button>
                </div>
            )
        } else {
            return (
                <div className={"some_lobby_player"}>
                    <EmoFace player={this.props.player}/>
                </div>
            )
        }
    }
}

export default SomeLobbyPlayer