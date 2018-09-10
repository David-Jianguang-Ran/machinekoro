import React from "react"

import Card from "./card"

/*
the below component has the following props:
    player
        - hand
        - landmarks
        - coin
*/
class SomePlayerMain extends React.Component{
    render(){
        // prepare land marks array
        let landmarks_array = []
        for (let key in this.props.player.landmarks) {
            let lm_suffix = null
            if (this.props.player.landmarks[key] === true) {
                lm_suffix = "_built"
            } else {
                lm_suffix = "_not_built"
            }
            let lm_real_name = key.concat(lm_suffix)
            landmarks_array.push()
        }

        return (
            <div className={"main_carousel_panel"}>
                <div className={"main_player_coin"}>

                </div>
                {landmarks_array.map(item => (
                    <Card name={item}/>
                ))}
                {this.props.player.hand.map(item => (
                    <Card name={item}/>
                ))}
            </div>
        )
    }
}

export default SomePlayerMain