from nameko.rpc import rpc


class EventThemeAnalyzer:
    # Vars

    name = "event_theme_analyzer"

    # TODO: inject it from lightweight db (SQLite i think)
    _TAGS = [
        ".NET",
        # TODO: place here more pre-defined tags
    ]

    # Logic

    def _analyze_event(event) -> dict:
        """Adds to event tags based on description

        Args:
            event (dict): clean event

        Returns:
            dict: clean event with tags
        """
        pass

    # API

    @rpc
    def analyze_events(self, events) -> list:
        """Produces list of tags for event based on description

        Args:
            events (list): clean events without tags

        Returns:
            list: of events with produced tags
        """
        return [self._analyze_event(event) for event in events]

    # TODO: we also need adminish API that allows us 
    #       to add and remove tags from the system
