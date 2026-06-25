import json
import time
import logging
import pika

from domain.exceptions import InvalidMessageError, SearchNotFoundError

from search.emails import EmailDeliveryError