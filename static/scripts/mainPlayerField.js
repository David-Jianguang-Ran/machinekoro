import React from "react"

import EmoBar from "./emoBar"
import SomePlayerMain from "./somePlayerMain"


class MainPlayerField extends React.Component{
    /*
    this component is a home made carousel
    props:
    - match_state
    - game_state

    children:
    - emoFaceBar
        props:
            displayed_player
            match_state
    - someMainPlayer
        props:
            player = game_state.players[num]
    */
    constructor(props){
        super(props)
        this.state = {
            "displayed_player": 0 // int player_num
        }
        this.setDisplayedPlayerCallback = this.setDisplayedPlayerCallback.bind(this)
    }
    setDisplayedPlayerCallback(player_num){
        this.setState({"displayed_player": player_num})
    }
    render(){
        return(
            <div>
                <EmoBar displayed_player={this.state.displayed_player}
                        match_state={this.props.match_state}
                        setDisplayedPlayerCallback={this.setDisplayedPlayerCallback()} />
                <SomePlayerMain player={this.props.game_state.players[this.state.displayed_player]}/>
            </div>
        )
    }
}

export default MainPlayerField

