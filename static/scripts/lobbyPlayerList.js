import React from "react"

import SomePlayerLobby from "./somePlayerLobby"

class LobbyPlayerList extends React.Component{
    /*
    This component displays all the players and their icon and emoji.
    For prime player, this component also can send messages to kick a particular player

    * props:
        - ws_manager
        - match_state
        - is_prime
    * Children:
        - SomePlayerLobby
            props:
            is_prime (the client)
            player
            kickPlayerCallBack
    */
    constructor(props){
        super(props)
        this.kickPlayerCallBack = this.kickPlayerCallBack.bind(this)
    }
    kickPlayerCallBack(target_player){
        /*
        This method sends a message with this.props.ws_manager to kick the player whos info is passed in
        :param: target_player: player_register obj
        :return: nothing, sends a ws message
        */
        let player_num = target_player.player_num
        const message = {
            key:"prime.player.command",
            cmd:"kick_player",
            target:player_num
        }
        this.props.ws_manager.sendJSON(message)
    }
    render(){

        return(
            <div className={"lobby_player_list"}>
                {Object.values(this.props.match_state).map((player) => (
                    <SomePlayerLobby key={player.player_num}
                                     is_prime={this.props.is_prime}
                                     player={player}
                                     kickPlayerCallBack={this.kickPlayerCallBack} />
                ))}
            </div>
        )
    }
}

export default LobbyPlayerList