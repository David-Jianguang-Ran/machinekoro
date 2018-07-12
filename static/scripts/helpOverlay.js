import React from 'react'

class HelpOverlay extends React.Component {
    constructor(props) {
        super(props);
        // attributes
        this.state = {
            expanded: false
        };
        this.buttonMode = (
            <div id={'help_expandable'}>
                <button id={'mr_help_button'} onClick={this.buttonClickHandler()}>Help!(Place Holder)</button>
            </div>
        );
        this.expandedMode = (
            <div id={'help_expandable'}>
                <button id={'mr_help_button'} onClick={this.buttonClickHandler()}>Help!(Place Holder)</button>
                <div>PlaceHolder Container for help swippable</div>
            </div>
        );
        // method bindings
        this.buttonClickHandler = this.buttonClickHandler.bind(this);
        this.render = this.render.bind(this); // I hope this binding doesn't break things invisible to me
    }
    buttonClickHandler(){
        this.state.expanded = ! this.state.expanded
    }
    render(){
        if (this.state.expanded) {
            return this.expandedMode
        } else {
            return this.buttonMode
        }
    }
}

export default HelpOverlay