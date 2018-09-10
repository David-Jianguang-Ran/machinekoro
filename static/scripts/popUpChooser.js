import React from "react"

import ExpandableButton from "./expandableButton"
import PopUpChoiceElement from "./popUpChoiceElement"

class popUpChooser extends ExpandableButton{
    /*
    props:
        icon_component
        choice_options
        submitChoiceCallback(choice_selected)
    */
    constructor(props){
        super(props)
        this.button = this.props.icon_component
        this.expanded = (
            <div>
                {this.props.choice_options.map(obj => (
                    <PopUpChoiceElement name={obj.name}
                                        value={obj.value}
                                        submitChoiceCallback={this.props.submitChoiceCallback}/>
                    ))}
            </div>
        )
    }
}