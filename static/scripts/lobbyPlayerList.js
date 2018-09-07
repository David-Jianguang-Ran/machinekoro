import React from "react"


class LobbyPlayers extends React.Component{
    /*
    This component displays all the players and their icon and emoji.
    For prime player, this component also can send messages to kick a particular player

    * props:
        - ws_manager
        - match_state
        - context
    * Children:
        - SomeLobbyPlayer
            props:
            is_prime (the client)
            player
            kickPlayerCallBack
    */
    kickPlayerCallBack(target_player){
        /*
        This method sends a message with this.props.ws_manager to kick the player whos info is passed in
        :param: target_player: player_register obj
        :return: nothing, sends a ws message
        */
        let player_num = target_player.num
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
                {this.props.match_state.map((player,key) => (
                    <SomeLobbyPlayer is_prime={this.props.cntext.is_prime}
                                     player={player}
                                     kickPlayerCallBack={this.kickPlayerCallBack} />
                ))}
            </div>
        )
    }
}

export default LobbyPlayers