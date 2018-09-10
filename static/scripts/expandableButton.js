import React from "react"

class ExpandableButtons extends React.Component {
    /*
    This is the template component for all button like objects that expand into a window when clicked
    when the button or anywhere outside the expanded area are clicked, the area will retract
    To use this button, add button component to this.button
    and add dialogue content to this.expanded
    */
    constructor(props){
        super(props)
        this.state = {
            expanded:false
        }
        this.element_id = Math.floor((Math.random()*10000)+1) // random element id for expanded component
        this.button = (
            // this is where to add the component content
            <div>

            </div>
        )
        this.expanded = (
            // this is where to add the component content
            <div>

            </div>
        )
        this.toggleExpansion = this.toggleExpansion.bind(this)
        this.retractWhenClickedOutside = this.retractWhenClickedOutside(this)
    }
    retractWhenClickedOutside(event){
        /*
        This method is a event listener that is added to the dom when this component mounts
        be sure to clean up in component will unmount
        */
        if (this.state.expanded === true && !event.target === document.getElementById(this.element_id)) {
            this.setState({expanded:false})
        }
    }
    componentDidMount(){
        document.addEventListener("click",this.retractWhenClickedOutside)
    }
    componentWillUnmount(){
        document.removeEventListener("click",this.retractWhenClickedOutside)
    }
    toggleExpansion(event){
        // this method toggles the expansion of the dialogue window
        this.setState({expanded: ! this.state.expanded})
    }
    render(){
        if (this.state.expanded === true) {
            return(
                <div>
                    <div className={"expandable_button"} onClick={this.toggleExpansion}>{this.button}</div>
                    <div className={"expanded_window"} id={this.element_id}>{this.expanded}</div>
                </div>
            )
        } else {
            return(
                <div>
                    <div className={"expandable_button"} onClick={this.toggleExpansion}>{this.button}</div>
                </div>
            )
        }
    }
}

export default ExpandableButtons