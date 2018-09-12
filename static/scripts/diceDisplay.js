import React from "react"

class DiceDisplay extends React.Component{
    /*
    props:
     - game_state

    */
    render(){
        if (this.props.game_state.temp_data["dice_roll"] !== null) {
            return(
                <div className={"utility_button"}>
                    <span>{this.props.game_state.temp_data["dice_roll"].toString()}</span>
                </div>
            )
        } else {
            return(
                <div className={"utility_button"}>
                    <span>...</span>
                </div>
            )
        }
    }
}

export default DiceDisplay