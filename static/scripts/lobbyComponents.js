import React from "react"

export class ShareBar extends React.Component{
    /*
    This component renders a join game link text for players to share
    */
    render(){
        let url ="http://127.0.0.1:8000/machinekoro/join"
        url.concat(this.props.context.match_id)
        return(
            <div id={"share_bar"}>
                <label>
                    Share the following link to invite friends to a game!
                    <input type={text} defaultValue={url}/>
                </label>
            </div>
        )
    }
}

export class LobbyPlayers extends React.Component{
    /*
    This component displays all the players and their icon and emoji.
    For prime player, this component also can send messages to kick a particular player

    * props:
        - match_state
        - context
    * Children:
        - SomeLobbyPlayer
            props: context

    */
    render(){
    }
}

import React from "react"

class someLobbyPlayer extends React.Component{
    render(){
        if (this.props.is_prime === true){
            return (
                <tr>

                </tr>
            )
        }
    }
}