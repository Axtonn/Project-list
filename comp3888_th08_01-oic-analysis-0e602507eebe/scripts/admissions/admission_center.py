"""
Define an enum for the Admission Center allowable in the database.
"""
from strenum import StrEnum


class AdmissionCenter(StrEnum):
    """
    Backend values for possible admission centers.
    """

    QTAC = 'QTAC'
    """
    Queensland Tertiary Admissions Centre. Lists courses for universities in
    Queensland.
    """

    SATAC = 'SATAC'
    """
    South Australian Tertiary Admissions Centre. Lists courses at South
    Australian and Northern Territorian Universities.
    """

    TISC = "TISC"
    """
    Tertiary Institutions Service Centre. Lists courses at Western Australian
    Universities.
    """

    UAC = 'UAC'
    """
    University Admissions Centre. Lists all universities in NSW, as well as
    some universities outside of New South Wales such as Griffith University.
    """

    UTAS = 'UTAS'
    """
    Univeristy of Tasmania (UTas). Central location for courses by accredited
    universities in Tasmania.
    """

    VTAC = 'VTAC'
    """
    Victorian Tertiary Admissions Centre. Lists courses at Victorian
    universities.
    """
