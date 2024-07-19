"""
This module defines the LayoutCreator class to be used to populate a Dash
application's layout.

CLASS
    LayoutCreator
        Defines a Dash application layout.

FUNCTIONS
    def create_layout(self) -> html.Div:
        Wrapper function to create entire layout.
    def _create_information_layout(self) -> html.Div:
        Wrapper function to create information layout portion.
    def _create_data_layout(self) -> html.Div:
        Wrapper function to create data layout portion.
    def _create_title() -> html.H1:
        Creates application title.
    def _create_description() -> html.P:
        Creates application description.
    def _create_search_dropdown() -> html.Div:
        Creates satellite search bar/dropdown.
    def _create_search_message() -> html.Div:
        Create empty html.Div for spacing purposes.
    def _create_button_celestrak() -> html.Div:
        Create button for updating CelesTrak TLEs.
    def _create_logo() -> html.Div:
        Create SpOC logo.
    def _create_celestrak_output() -> html.Div:
        Create output message for succesful CelesTrak TLE update.
    def _create_tabs() -> html.Div:
        Create right-side tabs for displaying information.
    def _create_contact_information() -> html.Footer:
        Create contact information footer.
"""
from dash import dcc, html

from wasp_tool_dash import utilities

STYLE_LEFT = {"margin": "10px 10px 10px 10px",
              "width": "100%", "height": "auto",
              "textAlign": "center",
              "align-items": "center",


              }
STYLE_TAB = {"margin": "10px 10px 10px 10px",
             "width": "100%", "height": "100%",
             "textAlign": "center",
             "align-items": "right",
             "box-shadow": "2px 2px 8px rgba(0, 0, 0, 0.2)"

             }


class LayoutCreator:
    """
    Defines a Dash application layout.
    """

    def create_layout(self, AWS_CLIENT, AWS_BUCKET_NAME,  PATH_KEY) -> html.Div:
        """
        Wrapper function to create entire layout.

        Parameters
        ----------
        self

        Returns
        -------
        html.Div
        """
        return html.Div(
            children=[
                html.Div(
                    className="row",
                    children=[
                        self._create_information_layout(
                            AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY
                        ),
                        self._create_data_layout(),
                    ],
                    style={"textAlign": "center", "align-items": "right"},
                )
            ]
        )

    def _create_information_layout(self,
                                   AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY
                                   ) -> html.Div:
        """
        Wrapper function to create information layout portion.

        Parameters
        ----------
        self

        Returns
        -------
        html.Div
        """
        return html.Div(
            className="three columns div-user-controls",
            children=[
                self._create_title(),
                self._create_description(),
                self._create_search_dropdown(
                    AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY
                ),
                self._create_search_message(),
                self._create_button_celestrak(),
                self._create_celestrak_output(),
                self._create_logo(),


            ],
            style={
                "textAlign": "center",
                "align-items": "left", "width": " 20%"},
        )

    def _create_data_layout(self) -> html.Div:
        """
        Wrapper function to create data layout portion.

        Parameters
        ----------
        self

        Returns
        -------
        html.Div
        """
        return html.Div(
            className="nine columns div-for-charts bg-grey",
            children=[
                html.Div(
                    id="page_content",
                    className="loader",
                    style=STYLE_LEFT,
                ),
                self._create_tabs(),
                self._create_contact_information(),
            ],
            style={"textAlign": "center", "align-items": "center"},
        )

    @staticmethod
    def _create_title() -> html.H1:
        """
        Creates application title.

        Returns
        -------
        html.H1
        """
        return html.H1("16th EWS W.A.S.P.", style=STYLE_LEFT)

    @staticmethod
    def _create_description() -> html.P:
        """
        Creates application description.

        Returns
        -------
        html.P
        """
        return html.P(
            """The Web Application for Satellite Pairing (WASP) consolidates pertinent
                    information to the satellite pair-building process. Enter a satellite below
                    to obtain its related data.""", style=STYLE_LEFT
        )

    @staticmethod
    def _create_search_dropdown(AWS_CLIENT, AWS_BUCKET_NAME, PATH_KEY) -> html.Div:
        """
        Creates satellite search bar/dropdown.

        Returns
        -------
        html.Div
        """
        return html.Div(
            className="search_dropdown",
            children=[
                html.Div("Satellite Search",
                         style=STYLE_LEFT),
                dcc.Dropdown(
                    id="sat-dropdown",
                    placeholder="INPUT A SATELLITE",
                    value="GALAXY 16",
                    options=utilities.populate_inputs(
                        AWS_CLIENT, AWS_BUCKET_NAME,  PATH_KEY
                    ),
                    style={"width": "100%",
                           "text-align": "center",
                           "margin": "10px,10px,10px,10px",
                           "font-size": "auto",
                           "align-items": "center", },

                )
            ],
        )

    @staticmethod
    def _create_button_celestrak() -> html.Div:
        """
        Create button for updating CelesTrak TLEs.

        Returns
        -------
        html.Div
        """
        return html.Div(
            className="button_celestrak",
            children=[
                html.Div(
                    "Click to Update TLE's",
                    style=STYLE_LEFT,
                ),
                html.Button(
                    "Update TLE's",
                    id="button-update-celestrak",
                    n_clicks=0,
                    style={

                        "width": "100%",
                        "background-color": "#00263A",
                        "color": "#DBE2E9",
                        "text-align": "center",
                        "margin": "10px,10px,10px,10px",
                        "font-size": "auto",
                        "align-items": "center",
                    },
                ),
            ],
        )

    @staticmethod
    def _create_search_message() -> html.Div:
        """
        Create empty html.Div for spacing purposes.

        Returns
        -------
        html.Div
        """
        return html.Div(id="search-message", style=STYLE_LEFT)

    @staticmethod
    def _create_logo() -> html.Div:
        """
        Create SpOC logo.

        Returns
        -------
        html.Div
        """
        return html.Div(
            className="logo",
            style={"padding": "20px", "margin": "20px"},
            children=[
                utilities.encode_image(
                    path=utilities.get_project_path().joinpath(
                        "wasp_tool_dash", "assets", "spoc_logo.png"
                    )
                ),
            ],


        )

    @staticmethod
    def _create_celestrak_output() -> html.Div:
        """
        Create output message for succesful CelesTrak TLE update.

        Returns
        -------
        html.Div
        """
        return html.Div(id="celestrak-output", style={"marginLeft": "5px", "height": "25px", "width": "auto"})

    @staticmethod
    def _create_current_output() -> html.Div:
        """
        Create output message for succesful current update.

        Returns
        -------
        html.Div
        """
        return html.Div(id="current-output", style={"marginLeft": "5px", "height": "25px", "width": "auto"})

    @staticmethod
    def _create_tabs() -> html.Div:
        """
        Create right-side tabs for displaying information.

        Returns
        -------
        html.Div
        """

        return html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(label="General Info", value="tab-general"),
                        dcc.Tab(label="TLE", value="tab-telemetry"),
                        dcc.Tab(label="Footprints", value="tab-footprints"),
                        dcc.Tab(label="Transponder Plans",
                                value="tab-freq_plans"),
                        dcc.Tab(label="Channels", value="tab-channels"),
                        LayoutCreator._create_dish_pointer(),
                    ],
                ),
                html.Div(id="tabs-content",),
            ],
            style=STYLE_TAB,
        )

    @staticmethod
    def _create_contact_information() -> html.Footer:
        """
        Create contact information footer.

        Returns
        -------
        html.Footer
        """
        return html.Footer(
            className="footer",
            children="""All information presented on this dashboard is aggregated and compiled
            from open-source, unclassified websites. The information is copyrighted and not
            approved for commercial or public use. The original sources for this information are
            https://www.satbeams.com/, https://www.lyngsat.com/, https://celestrak.org/, and
            http://frequencyplansatellites.altervista.org/. For more information or questions,
            please contact jason.tilley.3@spaceforce.mil.""",
            style={"font-style": "italic"},
        )

    @staticmethod
    def _create_dish_pointer() -> html.Div:
        """
        Create dish pointer tab.

        Returns
        -------
        html.Div
        """
        return dcc.Tab(
            label="Dish Pointer", value="tab-dishpointer", children=[


                html.Div(
                    children=[
                        html.P(""), html.P(id="azimuth-text"),
                        html.P(""), html.P(id="elevation-text"),

                    ],
                    style={"margin": "10px",
                           "padding": "10px", "color": "#00263A","display": "flex","align-items": "center","justify-content": "center"},
                ),
                html.Iframe(
                    id="map-frame",
                    width="100%",
                    height="500px",
                ),
                html.Div(
                    className="latlong",
                    children=[
                        html.Div(
                            children=[
                                html.P(" Latitude: "),
                                dcc.Input(
                                    id="latitude-input",
                                    type="number",
                                    value=0,
                                    step=0.0001
                                ),
                                html.P(" Longitude: "),
                                dcc.Input(
                                    id="longitude-input",
                                    type="number",
                                    value=0,
                                    step=0.0001
                                ),
                            ],
                            style={"margin": "10px",
                                   "padding": "10px", "color": "#00263A"},
                        ),
                        html.Div(
                            children=[
                                html.P("Input Location: "),
                                dcc.Input(
                                    id="location-input",
                                    type="text",
                                ),
                            ], style={"margin": "10px",
                                      "padding": "10px", "color": "#00263A"},),
                        html.Div(
                            className="button_update",
                            children=[
                                html.Button(
                                    "Update",
                                    id="button-update",
                                    n_clicks=0,
                                    style={
                                        "width": "auto",
                                        "background-color": "#00263A",
                                        "color": "white",
                                        "text-align": "center",
                                        "margin": "10px",
                                        "font-size": "auto",
                                    },
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )


