import React from 'react'

class Menu extends React.Component {
    constructor(props) {
        super(props);
        // attributes
        this.state = {
            expanded: false
        };
        this.buttonMode = (
            <div id={'hamburger_menu'}>
                <button id={'ms_menu_button'} onClick={this.buttonClickHandler()}>Hamburger!!!(Place Holder)</button>
            </div>
        );
        this.expandedMode = (
            <div id={'hamburger_menu'}>
                <button id={'ms_menu_button'} onClick={this.buttonClickHandler()}>Hamburger!!!(Place Holder)</button>
                <div>PlaceHolder Container for expanded hamburger menu</div>
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

export default Menu