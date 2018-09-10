import React from "react"

class PopUpChoiceElement extends React.Component{
    /*
    Props:
        value
        name
        visual_component
        submitChoiceCallback(choice)
    */
    constructor(props){
        super(props)
        this.handleSelect = this.handleSelect.bind(this)
    }
    handleSelect(event){
        this.props.submitChoiceCallback(this.props.value)
    }
    render(){
        let vis_comp = null
        if (this.props.visual_component !== null){
            vis_comp = this.props.visual_component
        }
        return(
            <div onClick={this.handleSelect}>
                {vis_comp}
                <span>{name}</span>
            </div>
        )
    }
}

export default PopUpChoiceElement