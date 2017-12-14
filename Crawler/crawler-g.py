from functools import partial

import scrapy


class Crawler(scrapy.Spider):
    name = "gobSpider"
    base_url = "https://www.educacion.gob.es/notasdecorte/"
    start_urls = [
        base_url + "busquedaSimple?codTipoEstudio=GRADO&nomTipoAcceso=Universidad&tipoUniv=T&chkEspana=C&codigosProv=00&method:busquedaSimple=Buscar&d-4809369-p=1&tipoAcceso=1"]

    def parse(self, response):
        table = response.xpath('//*[@id="ensenanzas"]/tbody/tr')
        #items = []
        for row in table:
            center_url = row.xpath('td[2]/a/@href').extract_first().strip()
            item = {
                'universidad': row.xpath('td[1]/a/text()').extract_first().strip(),
                'url_universidad': row.xpath('td[1]/a/@href').extract_first().strip(),
                'titulo': row.xpath('td[3]/a/text()').extract_first().strip(),
                'url_titulo': row.xpath('td[3]/a/@href').extract_first().strip(),
                'tipo': row.xpath('td[4]/text()').extract_first().strip(),
                'plazas': row.xpath('td[5]/text()').extract_first().strip(),
                'nota': row.xpath('td[6]/text()').extract_first().strip(),
                'creditos': row.xpath('td[9]/text()').extract_first().strip(),
                'precio_credito': row.xpath('td[10]/text()').extract_first().strip(),
            }
            self.clearDict(item)
            yield scrapy.Request(self.base_url + center_url, callback=partial(self.parse_sub, item))

        # Try to move to next page
        next_page = response.xpath('//*[@id="ver"]/span[2]/a[contains(text(),"Siguiente")]/@href')
        if next_page is not None:
            next_page = next_page.extract_first()
            yield scrapy.Request(self.base_url + next_page, callback=self.parse)

    def parse_sub(self, item, response):
        item['center'] = {
            'identificacion': {
                "centro": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[3]/strong/text()')),
                "codigo": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[4]/strong/text()'))
            },
            'ubicacion': {
                "comunidad_autonoma": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[5]/strong/text()')),
                "codigo_postal": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[6]/strong/text()')),
                "provincia": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[7]/strong/text()')),
                "telefono": self.getPhone(self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[8]/strong/text()'))),
                "localidad": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[9]/strong/text()')),
                "fax": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[10]/strong/text()')),
                "domicilio": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[11]/strong/text()')),
                "email": self.getValue(response.xpath('//*[@id="contenido"]/div[2]/ul/li[12]/strong/a/text()'))
            },
            'tipificacion': {
                "tipo_universidad": response.xpath('//*[@id="contenido"]/div[2]/ul/li[13]/strong/text()').extract_first().strip(),
                "tipo_centro": response.xpath('//*[@id="contenido"]/div[2]/ul/li[14]/strong/text()').extract_first().strip(),
                "calificacion_juridica": response.xpath('//*[@id="contenido"]/div[2]/ul/li[15]/strong/text()').extract_first().strip(),
                "vinculacion_universidad": response.xpath('//*[@id="contenido"]/div[2]/ul/li[16]/strong/text()').extract_first().strip()
            },
            'ensenanzas': []
        }
        table = response.xpath('//*[@id="contenido"]/table/tbody/tr')
        for row in table:
            teaching = {
                'codigo': self.getValue(row.xpath('td[1]/text()')),
                'ensenanza': self.getValue(row.xpath('td[2]/text()')),
                'ambito': self.getValue(row.xpath('td[3]/text()')),
                'nivel_estudio': self.getValue(row.xpath('td[4]/text()')),
                'situacion': self.getValue(row.xpath('td[5]/text()')),
            }
            item['center']['ensenanzas'].append(teaching)
        return item

    def clearDict(self, dic):
        toDel = []
        for key in dic:
            if dic[key] is None or dic[key] == "" or dic[key] == "-":
                toDel.append(key)
        for key in toDel:
            del dic[key]
        return dic

    def getValue(self, val):
        v1 = val.extract_first()
        if v1 is not None:
            v1 = v1.strip()
            if v1 == "-":
                return ""
            return v1
        return ""

    def getPhone(self, phone):
        return phone.replace(" ", "").replace(".", "")
